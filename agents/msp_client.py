"""
MSP Client
Thin HTTP client for interacting with the MSP Gateway
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class MSPClient:
    """Client for MSP Gateway API"""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8080",
        api_key: str = None,
        timeout: float = 30.0,
    ):
        """Initialize MSP Client

        Args:
            base_url: Base URL of the MSP Gateway
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def health_check(self) -> Dict[str, Any]:
        """Check gateway health

        Returns:
            Health check response
        """
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()

    def infer(
        self,
        tenant_id: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate inference

        Args:
            tenant_id: Tenant identifier
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            options: Additional options

        Returns:
            Inference response
        """
        data = {
            "tenant_id": tenant_id,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "options": options or {},
        }

        response = self.client.post("/v1/infer", json=data)
        response.raise_for_status()
        return response.json()

    def query_kb(
        self,
        tenant_id: str,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """Query knowledge base

        Args:
            tenant_id: Tenant identifier
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            include_metadata: Include document metadata

        Returns:
            KB query response
        """
        data = {
            "tenant_id": tenant_id,
            "query": query,
            "top_k": top_k,
            "filters": filters or {},
            "include_metadata": include_metadata,
        }

        response = self.client.post("/v1/query_kb", json=data)
        response.raise_for_status()
        return response.json()

    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        api_key: str,
        quota: Optional[Dict[str, int]] = None,
        policies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new tenant

        Args:
            tenant_id: Unique tenant identifier
            name: Tenant display name
            api_key: API key for the tenant
            quota: Resource quotas
            policies: Applied policy names
            metadata: Additional metadata

        Returns:
            Tenant response
        """
        data = {
            "tenant_id": tenant_id,
            "name": name,
            "api_key": api_key,
            "quota": quota
            or {
                "requests_per_minute": 60,
                "tokens_per_minute": 10000,
            },
            "policies": policies or [],
            "metadata": metadata or {},
        }

        response = self.client.post("/admin/tenants", json=data)
        response.raise_for_status()
        return response.json()

    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information

        Args:
            tenant_id: Tenant identifier

        Returns:
            Tenant response
        """
        response = self.client.get(f"/admin/tenants/{tenant_id}")
        response.raise_for_status()
        return response.json()

    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants

        Returns:
            List of tenant responses
        """
        response = self.client.get("/admin/tenants")
        response.raise_for_status()
        return response.json()

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        quota: Optional[Dict[str, int]] = None,
        policies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update tenant information

        Args:
            tenant_id: Tenant identifier
            name: Updated name
            quota: Updated quota
            policies: Updated policies
            metadata: Updated metadata
            active: Updated active status

        Returns:
            Updated tenant response
        """
        data = {}
        if name is not None:
            data["name"] = name
        if quota is not None:
            data["quota"] = quota
        if policies is not None:
            data["policies"] = policies
        if metadata is not None:
            data["metadata"] = metadata
        if active is not None:
            data["active"] = active

        response = self.client.patch(f"/admin/tenants/{tenant_id}", json=data)
        response.raise_for_status()
        return response.json()

    def delete_tenant(self, tenant_id: str):
        """Delete (deactivate) a tenant

        Args:
            tenant_id: Tenant identifier
        """
        response = self.client.delete(f"/admin/tenants/{tenant_id}")
        response.raise_for_status()

    def close(self):
        """Close the client connection"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    # Create client
    demo_api_key = os.getenv("MSP_API_KEY") or "your-api-key-here"
    client = MSPClient(api_key=demo_api_key)

    try:
        # Check health
        health = client.health_check()
        print(f"Gateway health: {health}")

        # Example inference
        result = client.infer(
            tenant_id="test-tenant",
            prompt="What is machine learning?",
            max_tokens=100,
        )
        print(f"Inference result: {result}")

    finally:
        client.close()


# Enhanced MSPClient with additional methods
class EnhancedMSPClient(MSPClient):
    """Enhanced MSP Client with advanced features."""

    def request_with_retry(
        self,
        method: str,
        endpoint: str,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff multiplier for retries
            **kwargs: Additional arguments for the request

        Returns:
            Response data

        Raises:
            httpx.HTTPStatusError: If all retries fail
        """
        import time

        last_exception = None
        for attempt in range(max_retries):
            try:
                response = self.client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2**attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")

        raise last_exception

    def batch_infer(
        self,
        tenant_id: str,
        prompts: List[str],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> List[Dict[str, Any]]:
        """Generate inferences for multiple prompts.

        Args:
            tenant_id: Tenant identifier
            prompts: List of input prompts
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            List of inference responses
        """
        results = []
        for prompt in prompts:
            result = self.infer(
                tenant_id=tenant_id,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            results.append(result)
        return results

    def stream_infer(
        self,
        tenant_id: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        """Stream inference response.

        Args:
            tenant_id: Tenant identifier
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Yields:
            Streamed response chunks
        """
        data = {
            "tenant_id": tenant_id,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }

        with self.client.stream("POST", "/v1/infer", json=data) as response:
            response.raise_for_status()
            for chunk in response.iter_text():
                if chunk:
                    yield chunk

    def get_usage_stats(
        self, tenant_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage statistics for a tenant.

        Args:
            tenant_id: Tenant identifier
            start_time: Start time (ISO format)
            end_time: End time (ISO format)

        Returns:
            Usage statistics
        """
        params = {"tenant_id": tenant_id}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        response = self.client.get("/admin/usage", params=params)
        response.raise_for_status()
        return response.json()

    def set_rate_limit(
        self, tenant_id: str, requests_per_minute: int, tokens_per_minute: int
    ) -> Dict[str, Any]:
        """Set rate limits for a tenant.

        Args:
            tenant_id: Tenant identifier
            requests_per_minute: Request rate limit
            tokens_per_minute: Token rate limit

        Returns:
            Updated tenant configuration
        """
        data = {
            "quota": {
                "requests_per_minute": requests_per_minute,
                "tokens_per_minute": tokens_per_minute,
            }
        }

        response = self.client.patch(f"/admin/tenants/{tenant_id}", json=data)
        response.raise_for_status()
        return response.json()

    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get information about available models.

        Args:
            model_id: Optional specific model ID

        Returns:
            Model information
        """
        if model_id:
            response = self.client.get(f"/v1/models/{model_id}")
        else:
            response = self.client.get("/v1/models")

        response.raise_for_status()
        return response.json()

    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key.

        Args:
            api_key: API key to validate

        Returns:
            True if valid, False otherwise
        """
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = self.client.get("/v1/validate", headers=headers)
            return response.status_code == 200
        except httpx.HTTPStatusError:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics.

        Returns:
            System metrics
        """
        response = self.client.get("/metrics")
        response.raise_for_status()
        return response.json()
