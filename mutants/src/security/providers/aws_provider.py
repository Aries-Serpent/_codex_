"""AWS Secrets Manager Provider implementation.

This module implements the SecretProvider interface for AWS Secrets Manager,
supporting secret rotation, retrieval, and management.

Part of PS-05 Enhancement: Multi-Provider Support - Priority 4
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any

from security.providers.base import (
    SecretProvider,
    ProviderType,
    SecretType,
    SecretMetadata,
    RotationResult,
    ValidationError,
    ProviderConfig,
    ProviderConfigError,
)

logger = logging.getLogger(__name__)

# Optional boto3 import
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.warning("boto3 not installed - AWS provider will be stub only")
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


class AWSSecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager provider.
    
    Supports:
    - Secret creation and rotation
    - Automatic rotation with Lambda
    - Version management
    - Tag-based organization
    
    Example:
        >>> config = ProviderConfig(
        ...     provider_type=ProviderType.AWS_SECRETS_MANAGER,
        ...     region="us-east-1",
        ...     aws_access_key_id="...",
        ...     aws_secret_access_key="..."
        ... )
        >>> provider = AWSSecretsManagerProvider(config)
        >>> result = provider.rotate_secret("my-secret")
    """
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_orig(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_1(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_2(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                None
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_3(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "XXboto3 required for AWS provider. Install with: pip install boto3XX"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_4(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for aws provider. install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_5(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "BOTO3 REQUIRED FOR AWS PROVIDER. INSTALL WITH: PIP INSTALL BOTO3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_6(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = None
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_7(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = None
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_8(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require(None)
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_9(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("XXregionXX")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_10(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("REGION")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_11(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = None
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_12(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "XXaws_access_key_idXX" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_13(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "AWS_ACCESS_KEY_ID" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_14(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" not in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_15(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = None
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_16(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["XXaws_access_key_idXX"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_17(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["AWS_ACCESS_KEY_ID"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_18(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get(None)
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_19(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("XXaws_access_key_idXX")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_20(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("AWS_ACCESS_KEY_ID")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_21(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = None
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_22(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["XXaws_secret_access_keyXX"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_23(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["AWS_SECRET_ACCESS_KEY"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_24(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get(None)
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_25(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("XXaws_secret_access_keyXX")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_26(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("AWS_SECRET_ACCESS_KEY")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_27(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = None
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_28(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            None,
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_29(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=None,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_30(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_31(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_32(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_33(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "XXsecretsmanagerXX",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_34(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "SECRETSMANAGER",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(f"AWS Secrets Manager provider initialized (region={self.region})")
    
    def xǁAWSSecretsManagerProviderǁ__init____mutmut_35(self, config: ProviderConfig):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            config: Provider configuration with AWS credentials
            
        Raises:
            ProviderConfigError: If boto3 not installed or config invalid
        """
        if not HAS_BOTO3:
            raise ProviderConfigError(
                "boto3 required for AWS provider. Install with: pip install boto3"
            )
        
        self.config = config
        self.region = config.require("region")
        
        # Create Secrets Manager client
        session_kwargs = {}
        if "aws_access_key_id" in config.config:
            session_kwargs["aws_access_key_id"] = config.get("aws_access_key_id")
            session_kwargs["aws_secret_access_key"] = config.get("aws_secret_access_key")
        
        self.client = boto3.client(
            "secretsmanager",
            region_name=self.region,
            **session_kwargs
        )
        
        logger.info(None)
    
    xǁAWSSecretsManagerProviderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁ__init____mutmut_1': xǁAWSSecretsManagerProviderǁ__init____mutmut_1, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_2': xǁAWSSecretsManagerProviderǁ__init____mutmut_2, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_3': xǁAWSSecretsManagerProviderǁ__init____mutmut_3, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_4': xǁAWSSecretsManagerProviderǁ__init____mutmut_4, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_5': xǁAWSSecretsManagerProviderǁ__init____mutmut_5, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_6': xǁAWSSecretsManagerProviderǁ__init____mutmut_6, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_7': xǁAWSSecretsManagerProviderǁ__init____mutmut_7, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_8': xǁAWSSecretsManagerProviderǁ__init____mutmut_8, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_9': xǁAWSSecretsManagerProviderǁ__init____mutmut_9, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_10': xǁAWSSecretsManagerProviderǁ__init____mutmut_10, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_11': xǁAWSSecretsManagerProviderǁ__init____mutmut_11, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_12': xǁAWSSecretsManagerProviderǁ__init____mutmut_12, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_13': xǁAWSSecretsManagerProviderǁ__init____mutmut_13, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_14': xǁAWSSecretsManagerProviderǁ__init____mutmut_14, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_15': xǁAWSSecretsManagerProviderǁ__init____mutmut_15, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_16': xǁAWSSecretsManagerProviderǁ__init____mutmut_16, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_17': xǁAWSSecretsManagerProviderǁ__init____mutmut_17, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_18': xǁAWSSecretsManagerProviderǁ__init____mutmut_18, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_19': xǁAWSSecretsManagerProviderǁ__init____mutmut_19, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_20': xǁAWSSecretsManagerProviderǁ__init____mutmut_20, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_21': xǁAWSSecretsManagerProviderǁ__init____mutmut_21, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_22': xǁAWSSecretsManagerProviderǁ__init____mutmut_22, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_23': xǁAWSSecretsManagerProviderǁ__init____mutmut_23, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_24': xǁAWSSecretsManagerProviderǁ__init____mutmut_24, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_25': xǁAWSSecretsManagerProviderǁ__init____mutmut_25, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_26': xǁAWSSecretsManagerProviderǁ__init____mutmut_26, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_27': xǁAWSSecretsManagerProviderǁ__init____mutmut_27, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_28': xǁAWSSecretsManagerProviderǁ__init____mutmut_28, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_29': xǁAWSSecretsManagerProviderǁ__init____mutmut_29, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_30': xǁAWSSecretsManagerProviderǁ__init____mutmut_30, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_31': xǁAWSSecretsManagerProviderǁ__init____mutmut_31, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_32': xǁAWSSecretsManagerProviderǁ__init____mutmut_32, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_33': xǁAWSSecretsManagerProviderǁ__init____mutmut_33, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_34': xǁAWSSecretsManagerProviderǁ__init____mutmut_34, 
        'xǁAWSSecretsManagerProviderǁ__init____mutmut_35': xǁAWSSecretsManagerProviderǁ__init____mutmut_35
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁ__init____mutmut_orig)
    xǁAWSSecretsManagerProviderǁ__init____mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁ__init__'
    
    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.AWS_SECRETS_MANAGER
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_orig(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_1(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = None
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_2(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=None,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_3(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=None,
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_4(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=None,
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_5(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=None,
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_6(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_7(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_8(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_9(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_10(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get(None),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_11(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("XXclient_request_tokenXX"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_12(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("CLIENT_REQUEST_TOKEN"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_13(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get(None),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_14(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("XXrotation_lambda_arnXX"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_15(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("ROTATION_LAMBDA_ARN"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_16(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get(None, {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_17(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", None),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_18(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get({}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_19(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", ),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_20(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("XXrotation_rulesXX", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_21(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("ROTATION_RULES", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_22(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=None,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_23(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=None,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_24(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=None,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_25(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata=None
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_26(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_27(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_28(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_29(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_30(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_31(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "XXversion_idXX": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_32(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "VERSION_ID": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_33(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["XXVersionIdXX"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_34(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["versionid"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_35(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VERSIONID"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_36(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "XXarnXX": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_37(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "ARN": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_38(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["XXARNXX"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_39(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["arn"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_40(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = None
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_41(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["XXErrorXX"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_42(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_43(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["ERROR"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_44(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["XXCodeXX"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_45(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_46(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["CODE"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_47(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = None
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_48(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["XXErrorXX"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_49(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_50(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["ERROR"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_51(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["XXMessageXX"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_52(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_53(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["MESSAGE"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_54(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(None)
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_55(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=None,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_56(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=None,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_57(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=None
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_58(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_59(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_60(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_61(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_62(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(None)
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_63(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=None,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_64(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=None,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_65(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=None
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_66(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_67(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_68(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_69(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_70(
        self,
        secret_id: str,
        **kwargs: Any
    ) -> RotationResult:
        """Rotate AWS secret.
        
        Args:
            secret_id: Secret name or ARN
            **kwargs: Optional parameters:
                - rotation_lambda_arn: Lambda function for rotation
                - rotation_rules: Rotation schedule rules
                
        Returns:
            RotationResult with rotation details
            
        Raises:
            RotationError: If rotation fails
        """
        try:
            # Trigger rotation
            response = self.client.rotate_secret(
                SecretId=secret_id,
                ClientRequestToken=kwargs.get("client_request_token"),
                RotationLambdaARN=kwargs.get("rotation_lambda_arn"),
                RotationRules=kwargs.get("rotation_rules", {}),
            )
            
            return RotationResult(
                success=True,
                old_secret_id=secret_id,
                new_secret_id=secret_id,  # Same ID, new version
                metadata={
                    "version_id": response["VersionId"],
                    "arn": response["ARN"],
                }
            )
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"AWS rotation failed ({error_code}): {error_msg}")
            
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=f"{error_code}: {error_msg}"
            )
        except Exception as e:
            logger.error(f"AWS rotation failed: {e}")
            return RotationResult(
                success=False,
                old_secret_id=secret_id,
                error_message=str(None)
            )
    
    xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_1': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_2': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_3': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_4': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_5': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_6': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_7': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_8': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_9': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_10': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_11': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_12': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_13': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_14': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_15': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_16': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_16, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_17': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_17, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_18': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_18, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_19': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_19, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_20': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_20, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_21': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_21, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_22': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_22, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_23': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_23, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_24': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_24, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_25': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_25, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_26': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_26, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_27': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_27, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_28': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_28, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_29': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_29, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_30': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_30, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_31': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_31, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_32': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_32, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_33': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_33, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_34': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_34, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_35': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_35, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_36': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_36, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_37': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_37, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_38': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_38, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_39': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_39, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_40': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_40, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_41': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_41, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_42': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_42, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_43': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_43, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_44': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_44, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_45': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_45, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_46': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_46, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_47': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_47, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_48': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_48, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_49': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_49, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_50': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_50, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_51': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_51, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_52': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_52, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_53': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_53, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_54': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_54, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_55': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_55, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_56': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_56, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_57': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_57, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_58': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_58, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_59': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_59, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_60': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_60, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_61': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_61, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_62': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_62, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_63': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_63, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_64': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_64, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_65': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_65, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_66': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_66, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_67': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_67, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_68': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_68, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_69': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_69, 
        'xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_70': xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_70
    }
    
    def rotate_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rotate_secret.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_orig)
    xǁAWSSecretsManagerProviderǁrotate_secret__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁrotate_secret'
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_orig(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_1(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=None)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_2(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return False
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_3(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = None
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_4(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["XXErrorXX"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_5(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_6(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["ERROR"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_7(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["XXCodeXX"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_8(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_9(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["CODE"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_10(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code != "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_11(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "XXResourceNotFoundExceptionXX":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_12(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "resourcenotfoundexception":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_13(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "RESOURCENOTFOUNDEXCEPTION":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_14(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return True
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_15(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(None) from e
        except Exception as e:
            raise ValidationError(f"Validation failed: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_16(
        self,
        secret_id: str,
        secret_value: Optional[str] = None
    ) -> bool:
        """Validate AWS secret exists and is accessible.
        
        Args:
            secret_id: Secret name or ARN
            secret_value: Not used (secret stored in AWS)
            
        Returns:
            True if secret is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Describe secret to check existence
            self.client.describe_secret(SecretId=secret_id)
            return True
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                return False
            raise ValidationError(f"Validation failed: {error_code}") from e
        except Exception as e:
            raise ValidationError(None) from e
    
    xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_1': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_2': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_3': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_4': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_5': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_6': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_7': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_8': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_9': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_10': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_11': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_12': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_13': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_14': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_15': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_16': xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_16
    }
    
    def validate_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_secret.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_orig)
    xǁAWSSecretsManagerProviderǁvalidate_secret__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁvalidate_secret'
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_orig(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_1(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = None
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_2(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=None)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_3(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = None
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_4(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get(None)
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_5(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("XXCreatedDateXX")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_6(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("createddate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_7(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CREATEDDATE")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_8(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at or not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_9(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_10(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = None
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_11(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=None)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_12(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = None
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_13(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get(None, created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_14(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", None)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_15(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get(created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_16(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", )
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_17(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("XXLastChangedDateXX", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_18(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("lastchangeddate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_19(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LASTCHANGEDDATE", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_20(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at or not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_21(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_22(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = None
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_23(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=None)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_24(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = None
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_25(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["XXKeyXX"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_26(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_27(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["KEY"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_28(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["XXValueXX"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_29(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_30(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["VALUE"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_31(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get(None, [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_32(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", None)
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_33(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get([])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_34(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", )
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_35(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("XXTagsXX", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_36(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_37(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("TAGS", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_38(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=None,
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_39(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=None,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_40(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=None,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_41(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=None,
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_42(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=None,
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_43(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=None,
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_44(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=None,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_45(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_46(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_47(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_48(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_49(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_50(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_51(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_52(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_53(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_54(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["XXNameXX"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_55(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_56(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["NAME"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_57(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at and datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_58(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(None),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_59(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at and datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_60(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(None),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_61(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get(None, False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_62(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", None),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_63(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get(False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_64(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", ),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_65(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("XXRotationEnabledXX", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_66(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("rotationenabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_67(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("ROTATIONENABLED", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_68(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", True),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(f"Failed to get metadata: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_69(self, secret_id: str) -> SecretMetadata:
        """Get AWS secret metadata.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            SecretMetadata with secret details
        """
        try:
            response = self.client.describe_secret(SecretId=secret_id)
            
            # Parse creation date
            created_at = response.get("CreatedDate")
            if created_at and not created_at.tzinfo:
                created_at = created_at.replace(tzinfo=UTC)
            
            # Parse last changed date
            updated_at = response.get("LastChangedDate", created_at)
            if updated_at and not updated_at.tzinfo:
                updated_at = updated_at.replace(tzinfo=UTC)
            
            # Parse tags
            tags = {
                tag["Key"]: tag["Value"]
                for tag in response.get("Tags", [])
            }
            
            return SecretMetadata(
                secret_id=response["Name"],
                secret_type=SecretType.GENERIC,
                provider=ProviderType.AWS_SECRETS_MANAGER,
                created_at=created_at or datetime.now(UTC),
                updated_at=updated_at or datetime.now(UTC),
                expires_at=None,  # AWS doesn't have expiration
                rotation_policy=response.get("RotationEnabled", False),
                tags=tags,
                scopes=None,
            )
            
        except ClientError as e:
            raise ValidationError(None) from e
    
    xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_1': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_2': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_3': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_4': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_5': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_6': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_7': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_8': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_9': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_10': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_11': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_12': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_13': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_14': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_15': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_16': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_16, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_17': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_17, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_18': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_18, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_19': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_19, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_20': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_20, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_21': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_21, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_22': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_22, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_23': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_23, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_24': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_24, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_25': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_25, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_26': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_26, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_27': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_27, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_28': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_28, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_29': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_29, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_30': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_30, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_31': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_31, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_32': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_32, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_33': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_33, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_34': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_34, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_35': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_35, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_36': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_36, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_37': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_37, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_38': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_38, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_39': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_39, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_40': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_40, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_41': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_41, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_42': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_42, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_43': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_43, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_44': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_44, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_45': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_45, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_46': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_46, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_47': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_47, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_48': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_48, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_49': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_49, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_50': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_50, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_51': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_51, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_52': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_52, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_53': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_53, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_54': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_54, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_55': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_55, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_56': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_56, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_57': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_57, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_58': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_58, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_59': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_59, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_60': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_60, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_61': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_61, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_62': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_62, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_63': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_63, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_64': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_64, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_65': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_65, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_66': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_66, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_67': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_67, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_68': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_68, 
        'xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_69': xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_69
    }
    
    def get_secret_metadata(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_secret_metadata.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_orig)
    xǁAWSSecretsManagerProviderǁget_secret_metadata__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁget_secret_metadata'
    
    def get_expiration(self, secret_id: str) -> Optional[datetime]:
        """Get secret expiration.
        
        AWS Secrets Manager doesn't have expiration concept.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            None (no expiration)
        """
        return None
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_orig(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_1(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = None
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_2(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=None)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_3(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "XXSecretStringXX" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_4(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "secretstring" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_5(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SECRETSTRING" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_6(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" not in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_7(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["XXSecretStringXX"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_8(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["secretstring"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_9(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SECRETSTRING"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_10(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode(None)
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_11(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(None).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_12(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["XXSecretBinaryXX"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_13(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["secretbinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_14(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SECRETBINARY"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_15(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("XXutf-8XX")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_16(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("UTF-8")
                
        except ClientError as e:
            raise ValidationError(f"Failed to get secret value: {e}") from e
    
    def xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_17(self, secret_id: str) -> str:
        """Get secret value from AWS.
        
        Args:
            secret_id: Secret name or ARN
            
        Returns:
            Secret value string
            
        Raises:
            ValidationError: If secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            
            # Return either SecretString or SecretBinary
            if "SecretString" in response:
                return response["SecretString"]
            else:
                import base64
                return base64.b64encode(response["SecretBinary"]).decode("utf-8")
                
        except ClientError as e:
            raise ValidationError(None) from e
    
    xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_1': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_2': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_3': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_4': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_5': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_6': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_7': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_8': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_9': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_10': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_11': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_12': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_13': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_14': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_15': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_16': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_16, 
        'xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_17': xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_17
    }
    
    def get_secret_value(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_secret_value.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_orig)
    xǁAWSSecretsManagerProviderǁget_secret_value__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁget_secret_value'
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_orig(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_1(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = None
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_2(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "XXNameXX": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_3(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_4(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "NAME": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_5(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "XXSecretStringXX": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_6(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "secretstring": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_7(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SECRETSTRING": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_8(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = None
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_9(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["XXDescriptionXX"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_10(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_11(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["DESCRIPTION"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_12(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = None
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_13(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["XXTagsXX"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_14(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_15(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["TAGS"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_16(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"XXKeyXX": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_17(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_18(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"KEY": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_19(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "XXValueXX": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_20(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_21(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "VALUE": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_22(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = None
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_23(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=None,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_24(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id=None,
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_25(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=None,
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_26(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=None,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_27(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata=None
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_28(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_29(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_30(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_31(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_32(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_33(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=False,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_34(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="XXXX",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_35(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["XXNameXX"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_36(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_37(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["NAME"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_38(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "XXarnXX": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_39(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "ARN": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_40(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["XXARNXX"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_41(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["arn"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_42(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "XXversion_idXX": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_43(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "VERSION_ID": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_44(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["XXVersionIdXX"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_45(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["versionid"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_46(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VERSIONID"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_47(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=None,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_48(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id=None,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_49(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=None
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_50(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_51(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_52(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_53(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=True,
                old_secret_id="",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_54(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="XXXX",
                error_message=str(e)
            )
    
    def xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_55(
        self,
        name: str,
        secret_value: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> RotationResult:
        """Create new AWS secret.
        
        Args:
            name: Secret name
            secret_value: Secret value (string or JSON)
            description: Optional description
            tags: Optional tags
            
        Returns:
            RotationResult with creation details
        """
        try:
            create_kwargs = {
                "Name": name,
                "SecretString": secret_value,
            }
            
            if description:
                create_kwargs["Description"] = description
            
            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]
            
            response = self.client.create_secret(**create_kwargs)
            
            return RotationResult(
                success=True,
                old_secret_id="",
                new_secret_id=response["Name"],
                new_secret_value=secret_value,
                metadata={
                    "arn": response["ARN"],
                    "version_id": response["VersionId"],
                }
            )
            
        except ClientError as e:
            return RotationResult(
                success=False,
                old_secret_id="",
                error_message=str(None)
            )
    
    xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_1': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_2': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_3': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_4': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_5': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_6': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_7': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_8': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_9': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_10': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_11': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_12': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_13': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_14': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_15': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_16': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_16, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_17': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_17, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_18': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_18, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_19': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_19, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_20': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_20, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_21': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_21, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_22': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_22, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_23': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_23, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_24': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_24, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_25': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_25, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_26': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_26, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_27': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_27, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_28': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_28, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_29': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_29, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_30': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_30, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_31': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_31, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_32': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_32, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_33': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_33, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_34': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_34, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_35': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_35, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_36': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_36, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_37': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_37, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_38': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_38, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_39': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_39, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_40': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_40, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_41': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_41, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_42': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_42, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_43': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_43, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_44': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_44, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_45': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_45, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_46': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_46, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_47': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_47, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_48': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_48, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_49': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_49, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_50': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_50, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_51': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_51, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_52': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_52, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_53': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_53, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_54': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_54, 
        'xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_55': xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_55
    }
    
    def create_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    create_secret.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_orig)
    xǁAWSSecretsManagerProviderǁcreate_secret__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁcreate_secret'
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_orig(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_1(
        self,
        secret_id: str,
        recovery_window_days: int = 31
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_2(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=None,
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_3(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=None
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_4(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_5(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_6(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=recovery_window_days
            )
            return False
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_7(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(None)
            return False
    
    def xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_8(
        self,
        secret_id: str,
        recovery_window_days: int = 30
    ) -> bool:
        """Delete AWS secret (with recovery window).
        
        Args:
            secret_id: Secret name or ARN
            recovery_window_days: Days before permanent deletion
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_secret(
                SecretId=secret_id,
                RecoveryWindowInDays=recovery_window_days
            )
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete secret: {e}")
            return True
    
    xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_1': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_2': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_3': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_4': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_5': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_6': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_7': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_8': xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_8
    }
    
    def delete_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete_secret.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_orig)
    xǁAWSSecretsManagerProviderǁdelete_secret__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁdelete_secret'
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_orig(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_1(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = None
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_2(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = None
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_3(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator(None)
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_4(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("XXlist_secretsXX")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_5(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("LIST_SECRETS")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_6(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = None
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_7(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append(None)
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_8(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "XXKeyXX": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_9(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_10(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "KEY": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_11(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "XXtag-keyXX",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_12(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "TAG-KEY",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_13(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "XXValuesXX": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_14(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_15(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "VALUES": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_16(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append(None)
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_17(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "XXKeyXX": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_18(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_19(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "KEY": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_20(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "XXtag-valueXX",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_21(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "TAG-VALUE",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_22(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "XXValuesXX": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_23(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_24(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "VALUES": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_25(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=None):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_26(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["XXSecretListXX"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_27(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["secretlist"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_28(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SECRETLIST"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_29(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = None
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_30(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(None)
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_31(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["XXNameXX"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_32(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_33(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["NAME"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_34(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(None)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_35(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(None)
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_36(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(None).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_37(
        self,
        filter_tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager.
        
        Args:
            filter_tags: Optional tag filters
            
        Returns:
            List of SecretMetadata
        """
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")
            
            # Build filters
            filters = []
            if filter_tags:
                for key, value in filter_tags.items():
                    filters.append({
                        "Key": "tag-key",
                        "Values": [key]
                    })
                    filters.append({
                        "Key": "tag-value",
                        "Values": [value]
                    })
            
            # Paginate through results
            for page in paginator.paginate(Filters=filters):
                for secret in page["SecretList"]:
                    try:
                        metadata = self.get_secret_metadata(secret["Name"])
                        secrets.append(metadata)
                    except Exception as e:
                        # Don't log secret names for security
                        logger.warning(f"Failed to get metadata for a secret: {type(e).__name__}")
            
            return secrets
            
        except ClientError as e:
            logger.error(None)
            return []
    
    xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_1': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_1, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_2': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_2, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_3': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_3, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_4': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_4, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_5': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_5, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_6': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_6, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_7': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_7, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_8': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_8, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_9': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_9, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_10': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_10, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_11': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_11, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_12': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_12, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_13': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_13, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_14': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_14, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_15': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_15, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_16': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_16, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_17': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_17, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_18': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_18, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_19': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_19, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_20': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_20, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_21': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_21, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_22': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_22, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_23': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_23, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_24': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_24, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_25': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_25, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_26': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_26, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_27': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_27, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_28': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_28, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_29': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_29, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_30': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_30, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_31': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_31, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_32': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_32, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_33': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_33, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_34': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_34, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_35': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_35, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_36': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_36, 
        'xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_37': xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_37
    }
    
    def list_secrets(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_orig"), object.__getattribute__(self, "xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_secrets.__signature__ = _mutmut_signature(xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_orig)
    xǁAWSSecretsManagerProviderǁlist_secrets__mutmut_orig.__name__ = 'xǁAWSSecretsManagerProviderǁlist_secrets'
