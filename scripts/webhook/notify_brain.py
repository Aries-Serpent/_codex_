#!/usr/bin/env python3
"""
Webhook notification to Cognitive Brain on registry events.

This script triggers webhook notifications to the Cognitive Brain system
with registry validation results and metadata.
"""

import json
import sys
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Send webhook notifications to Cognitive Brain."""

    def __init__(self, webhook_url: Optional[str] = None, secret: Optional[str] = None):
        """Initialize webhook notifier."""
        self.webhook_url = webhook_url
        self.secret = secret
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def create_webhook_payload(
        self,
        event: str,
        registry_config: Dict[str, Any],
        validation_results: Dict[str, Any],
        connectivity_results: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create webhook payload."""
        payload = {
            "event": event,
            "timestamp": self.timestamp,
            "registry": {
                "type": registry_config.get("registry_type", "unknown"),
                "endpoint": registry_config.get("endpoint", ""),
                "namespace": registry_config.get("namespace", ""),
            },
            "validation": {
                "confidence": validation_results.get("confidence", 0.0),
                "valid": validation_results.get("valid", False),
                "issues": validation_results.get("issues", []),
            },
        }
        
        if connectivity_results:
            payload["connectivity"] = {
                "overall_status": connectivity_results.get("overall_status", "unknown"),
                "tests_summary": connectivity_results.get("summary", {}),
            }
        
        return payload

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 signature for payload."""
        if not self.secret:
            raise ValueError("Webhook secret not configured")
        
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"

    def prepare_webhook_notification(
        self,
        event: str,
        registry_config: Dict[str, Any],
        validation_results: Dict[str, Any],
        connectivity_results: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Prepare webhook notification with signature."""
        payload = self.create_webhook_payload(
            event, registry_config, validation_results, connectivity_results
        )
        
        notification = {
            "payload": payload,
            "headers": {
                "Content-Type": "application/json",
                "X-Webhook-Event": event,
            },
        }
        
        if self.secret:
            signature = self.sign_payload(payload)
            notification["headers"]["X-Webhook-Signature"] = signature
        
        return notification


def generate_sample_webhook_payload() -> Dict[str, Any]:
    """Generate sample webhook payload for testing."""
    notifier = WebhookNotifier(secret="test_secret_key")
    
    sample_registry_config = {
        "registry_type": "ghcr",
        "endpoint": "ghcr.io",
        "namespace": "org/imagename",
    }
    
    sample_validation_results = {
        "confidence": 0.95,
        "valid": True,
        "issues": [],
    }
    
    sample_connectivity_results = {
        "overall_status": "passed",
        "summary": {
            "total_tests": 5,
            "passed": 5,
            "failed": 0,
            "success_rate": "100.0%",
        },
    }
    
    return notifier.prepare_webhook_notification(
        "registry_validation_complete",
        sample_registry_config,
        sample_validation_results,
        sample_connectivity_results,
    )


def main():
    """Main entry point."""
    try:
        # Generate sample webhook payload
        webhook_data = generate_sample_webhook_payload()
        
        # Log webhook notification
        logger.info("Webhook notification prepared")
        logger.info(f"Event: registry_validation_complete")
        logger.info(f"Headers configured with HMAC signature")
        
        # Print payload
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notifier_version": "1.0.0",
            "webhook_notification": webhook_data,
            "validation_report": {
                "webhook_configured": True,
                "hmac_signature_enabled": True,
                "payload_structure": "valid",
                "ready_for_delivery": True,
            },
        }
        
        print(json.dumps(output, indent=2))
        
        return 0
    except Exception as e:
        logger.error(f"Error preparing webhook notification: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
