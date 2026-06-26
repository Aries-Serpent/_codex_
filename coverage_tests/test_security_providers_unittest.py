import os
from __future__ import annotations

import base64
import types
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from security.provider_factory import ProviderFactory, create_provider_from_env
from security.providers import aws_provider
from security.providers.base import (
    ProviderConfig,
    ProviderConfigError,
    ProviderType,
    ValidationError,
)


class ProviderFactoryCoverageTests(unittest.TestCase):
    def test_create_from_dict_validation(self) -> None:
        with self.assertRaises(ProviderConfigError):
            ProviderFactory.create_from_dict({})
        with self.assertRaises(ProviderConfigError):
            ProviderFactory.create_from_dict({"provider_type": "nope"})

    def test_validate_config_branches(self) -> None:
        self.assertTrue(
            ProviderFactory.validate_config(
                ProviderConfig(provider_type=ProviderType.GITHUB, token=os.environ.get("TEST_GITHUB_TOKEN", "mock_token"))
            )
        )
        with self.assertRaises(ProviderConfigError):
            ProviderFactory.validate_config(ProviderConfig(provider_type=ProviderType.AWS_SECRETS_MANAGER))
        with self.assertRaises(ProviderConfigError):
            ProviderFactory.validate_config(ProviderConfig(provider_type=ProviderType.AZURE_KEY_VAULT))
        with self.assertRaises(ProviderConfigError):
            ProviderFactory.validate_config(ProviderConfig(provider_type=ProviderType.HASHICORP_VAULT))

    def test_create_provider_from_env_and_availability(self) -> None:
        fake_github = types.SimpleNamespace(GitHubTokenProvider=lambda config: ("github", config))
        fake_aws = types.SimpleNamespace(AWSSecretsManagerProvider=lambda config: ("aws", config))
        fake_env = types.SimpleNamespace(EnvironmentProvider=lambda config: ("env", config))
        with patch.dict(
            "sys.modules",
            {
                "security.providers.github_provider": fake_github,
                "security.providers.aws_provider": fake_aws,
                "security.providers.environment_provider": fake_env,
            },
        ):
            gh = create_provider_from_env(ProviderType.GITHUB)
            aws = create_provider_from_env(ProviderType.AWS_SECRETS_MANAGER)
            env = ProviderFactory.create_provider(
                ProviderConfig(provider_type=ProviderType.ENVIRONMENT)
            )
            available = ProviderFactory.get_available_providers()

        self.assertEqual(gh[0], "github")
        self.assertEqual(aws[0], "aws")
        self.assertEqual(env[0], "env")
        self.assertIn(ProviderType.ENVIRONMENT, available)

        with self.assertRaises(ProviderConfigError):
            create_provider_from_env(ProviderType.HASHICORP_VAULT)


class AWSProviderCoverageTests(unittest.TestCase):
    def _provider(self) -> aws_provider.AWSSecretsManagerProvider:
        fake_client = MagicMock()
        with (
            patch.object(aws_provider, "HAS_BOTO3", True),
            patch.object(aws_provider.boto3, "client", return_value=fake_client),
        ):
            provider = aws_provider.AWSSecretsManagerProvider(
                ProviderConfig(provider_type=ProviderType.AWS_SECRETS_MANAGER, region="us-east-1")
            )
        provider.client = fake_client
        return provider

    def test_rotate_validate_and_values(self) -> None:
        provider = self._provider()
        provider.client.rotate_secret.return_value = {"VersionId": "v1", "ARN": "arn:1"}
        ok = provider.rotate_secret("sec1")
        self.assertTrue(ok.success)

        class _ClientError(Exception):
            def __init__(self, code: str, msg: str):
                self.response = {"Error": {"Code": code, "Message": msg}}

        with patch.object(aws_provider, "ClientError", _ClientError):
            provider.client.rotate_secret.side_effect = _ClientError("Boom", "bad")
            failed = provider.rotate_secret("sec2")
            self.assertFalse(failed.success)
            self.assertIn("Boom", failed.error_message or "")

            provider.client.describe_secret.side_effect = _ClientError("ResourceNotFoundException", "x")
            self.assertFalse(provider.validate_secret("missing"))
            provider.client.describe_secret.side_effect = _ClientError("AccessDenied", "x")
            with self.assertRaises(ValidationError):
                provider.validate_secret("denied")

        provider.client.get_secret_value.return_value = {"SecretString": "plain"}  # pragma: allowlist secret
        self.assertEqual(provider.get_secret_value("sec"), "plain")  # pragma: allowlist secret
        provider.client.get_secret_value.return_value = {"SecretBinary": b"bin"}
        self.assertEqual(provider.get_secret_value("sec"), base64.b64encode(b"bin").decode("utf-8"))

    def test_metadata_create_delete_list(self) -> None:
        provider = self._provider()
        naive = datetime(2026, 1, 1, 0, 0, 0)
        provider.client.describe_secret.return_value = {
            "Name": "sec-meta",
            "CreatedDate": naive,
            "LastChangedDate": naive,
            "Tags": [{"Key": "team", "Value": "sec"}],
            "RotationEnabled": True,
        }
        metadata = provider.get_secret_metadata("sec-meta")
        self.assertEqual(metadata.secret_id, "sec-meta")
        self.assertEqual(metadata.tags, {"team": "sec"})

        provider.client.create_secret.return_value = {"Name": "n1", "ARN": "arn", "VersionId": "v2"}
        created = provider.create_secret("n1", "value", description="d", tags={"k": "v"})
        self.assertTrue(created.success)

        provider.client.delete_secret.return_value = {}
        self.assertTrue(provider.delete_secret("n1"))
        class _ClientError(Exception):
            pass

        with patch.object(aws_provider, "ClientError", _ClientError):
            provider.client.delete_secret.side_effect = _ClientError("boom")
            self.assertFalse(provider.delete_secret("n1"))

        provider.client.get_paginator.return_value.paginate.return_value = [
            {"SecretList": [{"Name": "sec-meta"}]}
        ]
        listed = provider.list_secrets(filter_tags={"team": "sec"})
        self.assertEqual(len(listed), 1)
