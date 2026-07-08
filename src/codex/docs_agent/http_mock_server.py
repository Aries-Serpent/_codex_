"""
HTTP Mock Server Module for Docs Agent

Provides mock HTTP endpoints for testing and development, simulating
real API responses with realistic latency and error patterns.

Authority: Lane 3 Unified Documentation Agent
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from flask import Flask, jsonify, request

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not installed. Install with: pip install flask")


class MockHTTPServer:
    """Mock HTTP server for documentation API endpoints"""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, enable_latency: bool = True):
        """Initialize mock server

        Args:
            host: Server host
            port: Server port
            enable_latency: Whether to simulate network latency
        """
        self.host = host
        self.port = port
        self.enable_latency = enable_latency
        self.app = None
        self.endpoints: dict[str, Any] = {}
        self.call_count: dict[str, int] = {}
        self.error_rate = 0.0  # 0-1, probability of error

        self._setup_app()

    def _setup_app(self):
        """Set up Flask application"""
        if not FLASK_AVAILABLE:
            logger.warning("Flask not available, mock server features limited")
            return

        self.app = Flask(__name__)

        # Register default endpoints
        self.register_endpoint("/api/v1/docs/search", self._handle_search, methods=["POST"])

        self.register_endpoint("/api/v1/docs/<doc_id>", self._handle_get_doc, methods=["GET"])

        self.register_endpoint("/api/v1/docs", self._handle_list_docs, methods=["GET"])

    def register_endpoint(self, path: str, handler: Callable, methods: Optional[List[str]] = None):
        """Register a mock endpoint

        Args:
            path: URL path
            handler: Handler function
            methods: HTTP methods
        """
        if methods is None:
            methods = ["GET"]

        self.endpoints[path] = {
            "handler": handler,
            "methods": methods,
        }

        logger.debug(f"Registered endpoint: {path}")

    def _simulate_latency(self):
        """Simulate network latency"""
        if not self.enable_latency:
            return

        # Simulate latency: 50ms baseline + 20-100ms random
        latency = 0.05 + random.uniform(0.02, 0.1)
        time.sleep(latency)

    def _check_error_condition(self) -> Optional[Dict[str, Any]]:
        """Check if request should error"""
        if random.random() < self.error_rate:
            errors = [
                {"status": 500, "message": "Internal Server Error"},
                {"status": 503, "message": "Service Unavailable"},
                {"status": 429, "message": "Too Many Requests"},
            ]
            return random.choice(errors)
        return None

    def _handle_search(self) -> Dict[str, Any]:
        """Handle search endpoint"""
        self._simulate_latency()

        # Check error condition
        error = self._check_error_condition()
        if error:
            return jsonify({"error": error["message"]}), error["status"]

        query = request.get_json().get("query", "")
        limit = request.get_json().get("limit", 10)

        self.call_count["search"] = self.call_count.get("search", 0) + 1

        # Return mock search results
        results = [
            {
                "id": f"doc-{i}",
                "type": "section",
                "title": f"Result {i}: {query}",
                "content": f'Content matching query "{query}"...',
                "score": 0.9 - (i * 0.05),
            }
            for i in range(min(limit, 10))
        ]

        return jsonify(
            {
                "query": query,
                "results": results,
                "total": len(results),
            }
        )

    def _handle_get_doc(self, doc_id: str) -> Dict[str, Any]:
        """Handle get document endpoint"""
        self._simulate_latency()

        error = self._check_error_condition()
        if error:
            return jsonify({"error": error["message"]}), error["status"]

        self.call_count["get_doc"] = self.call_count.get("get_doc", 0) + 1

        return jsonify(
            {
                "id": doc_id,
                "type": "document",
                "title": f"Document {doc_id}",
                "content": f"Content for {doc_id}...",
                "created_at": datetime.now().isoformat(),
            }
        )

    def _handle_list_docs(self) -> Dict[str, Any]:
        """Handle list documents endpoint"""
        self._simulate_latency()

        error = self._check_error_condition()
        if error:
            return jsonify({"error": error["message"]}), error["status"]

        limit = request.args.get("limit", 50, type=int)

        self.call_count["list_docs"] = self.call_count.get("list_docs", 0) + 1

        docs = [
            {
                "id": f"doc-{i}",
                "type": "document",
                "title": f"Document {i}",
            }
            for i in range(min(limit, 50))
        ]

        return jsonify(
            {
                "documents": docs,
                "total": len(docs),
            }
        )

    def set_error_rate(self, rate: float):
        """Set error rate (0.0 - 1.0)

        Args:
            rate: Error probability
        """
        self.error_rate = max(0.0, min(1.0, rate))
        logger.info(f"Error rate set to {self.error_rate:.1%}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics

        Returns:
            Server statistics
        """
        return {
            "host": self.host,
            "port": self.port,
            "endpoints_registered": len(self.endpoints),
            "calls_by_endpoint": self.call_count.copy(),
            "total_calls": sum(self.call_count.values()),
            "error_rate": self.error_rate,
        }

    def run(self, debug: bool = False):
        """Run the mock server

        Args:
            debug: Enable Flask debug mode
        """
        if not FLASK_AVAILABLE:
            logger.error("Flask not available, cannot start server")
            return

        logger.info(f"Starting mock server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)


class MockResponseBuilder:
    """Builder for mock API responses"""

    @staticmethod
    def search_response(
        query: str, results: int = 10, include_errors: bool = False
    ) -> Dict[str, Any]:
        """Build mock search response

        Args:
            query: Search query
            results: Number of results
            include_errors: Include error scenarios

        Returns:
            Mock response
        """
        items = [
            {
                "id": f"result-{i}",
                "type": "section",
                "title": f'Search Result {i} for "{query}"',
                "content": f'Content snippet matching "{query}"...',
                "score": max(0.5, 0.99 - (i * 0.05)),
                "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
            }
            for i in range(results)
        ]

        response = {
            "status": "success",
            "query": query,
            "results": items,
            "total": len(items),
            "timestamp": datetime.now().isoformat(),
        }

        if include_errors and random.random() < 0.1:
            response["warnings"] = [
                "Query took longer than usual to process",
                "Some results may be stale",
            ]

        return response

    @staticmethod
    def document_response(doc_id: str) -> Dict[str, Any]:
        """Build mock document response

        Args:
            doc_id: Document ID

        Returns:
            Mock response
        """
        return {
            "status": "success",
            "document": {
                "id": doc_id,
                "type": "document",
                "title": f"Document: {doc_id}",
                "content": f"Full content for {doc_id}...",
                "metadata": {
                    "category": "API Reference",
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                },
                "sections": [
                    {"id": "sec-001", "title": "Introduction"},
                    {"id": "sec-002", "title": "Getting Started"},
                    {"id": "sec-003", "title": "API Reference"},
                ],
            },
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def error_response(
        error_code: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build error response

        Args:
            error_code: Error code
            message: Error message
            details: Additional details

        Returns:
            Error response
        """
        response = {
            "status": "error",
            "error": {
                "code": error_code,
                "message": message,
            },
            "timestamp": datetime.now().isoformat(),
        }

        if details:
            response["error"]["details"] = details

        return response
