"""
CI Emergency Response Agent - Token Integration Example

Full working example demonstrating token acquisition, scope validation,
and emergency workflow dispatch for the ci-emergency-response-agent.

Key Concepts:
- Level 3 (CODEX_MASTER_KEY) token requirement
- Scopes: repo, workflow, actions:write
- NO FALLBACK - must fail safely if token unavailable
- Emergency operations pattern
"""

import logging
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmergencyResponse:
    status: str
    run_id: Optional[int] = None
    message: str = ""
    timestamp: str = ""


class CIEmergencyResponseAgent:
    """Emergency response for blocking CI failures."""
    
    def __init__(self):
        from scripts.ci._token_resolver import get_token, validate_scope
        
        # Requires Level 3 - NO fallback
        self.token = get_token(required_elevated=True, require_level=3)
        if not self.token:
            raise RuntimeError("CI Emergency agent requires Level 3 token")
        
        validate_scope(self.token, ['repo', 'workflow', 'actions:write'])
    
    def dispatch_emergency_workflow(
        self,
        repo: str,
        workflow_id: str,
        inputs: Optional[Dict] = None,
        reason: str = ""
    ) -> EmergencyResponse:
        """Dispatch emergency workflow."""
        inputs = inputs or {}
        
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.post(
                url,
                json={"ref": "main", "inputs": inputs},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(
                "emergency_workflow_dispatched",
                extra={"repo": repo, "workflow": workflow_id, "reason": reason}
            )
            
            return EmergencyResponse(
                status="success",
                message=f"Workflow {workflow_id} dispatched",
                timestamp=datetime.utcnow().isoformat()
            )
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise RuntimeError("Insufficient scope for workflow dispatch")
            raise


if __name__ == "__main__":
    agent = CIEmergencyResponseAgent()
    result = agent.dispatch_emergency_workflow(
        repo="owner/repo",
        workflow_id="emergency-fix.yml",
        reason="Critical CI failure"
    )
    print(f"Result: {result}")
