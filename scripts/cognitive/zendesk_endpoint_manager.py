#!/usr/bin/env python3
"""
Zendesk Endpoint Manager

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/zendesk_endpoint_manager.py [options]

    Examples:
    $ python scripts/cognitive/zendesk_endpoint_manager.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from requests import Session as _Session
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("zendesk_endpoint_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ZendeskEndpointManager")

# Constants
DEFAULT_OUTPUT_DIR = "zendesk_exports"
MAX_RETRIES = 3
BASE_WAIT_TIME = 2  # seconds
CACHE_SUBDIR_NAME = ".cache_data"
CACHE_FILE_NAME = "api_data_cache.json"
CACHE_EXPIRY_DAYS = 3
CACHE_EXPIRY_SECONDS = CACHE_EXPIRY_DAYS * 24 * 60 * 60

# Endpoint Categories
CORE_ENDPOINTS = [
    "users", "groups", "organizations", "tickets", "ticket_fields"
]

SETTINGS_ENDPOINTS = [
    "triggers", "automations", "macros", "views", "slas",
    "roles", "schedules", "targets", "webhooks", "apps"
]

ALL_ENDPOINTS = CORE_ENDPOINTS + SETTINGS_ENDPOINTS


class ZendeskEndpointManager:
    """
    Zendesk Endpoint Manager for Cognitive Brain Integration
    Extends Unified Mapper with comprehensive endpoint management
    """

    def __init__(
        self,
        subdomain: str,
        email: str,
        api_token: str,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        enable_cache: bool = True
    ):
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token
        self.output_dir = Path(output_dir)
        self.enable_cache = enable_cache

        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self.session = _Session()
        self.session.auth = (f"{email}/token", api_token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Cache setup
        self.cache_dir = self.output_dir / CACHE_SUBDIR_NAME
        self.cache_file = self.cache_dir / CACHE_FILE_NAME
        self.cache: Dict[str, Any] = {}

        if self.enable_cache:
            self._load_cache()

        logger.info(f"Initialized ZendeskEndpointManager for {subdomain}")

    def _load_cache(self):
        """Load cache from file if it exists and is valid"""
        if not self.cache_file.exists():
            logger.info("No cache file found, starting fresh")
            return

        try:
            with open(self.cache_file) as f:
                self.cache = json.load(f)

            # Check cache expiry
            cache_time = self.cache.get('_metadata', {}).get('timestamp')
            if cache_time:
                cache_age = time.time() - cache_time
                if cache_age > CACHE_EXPIRY_SECONDS:
                    logger.warning(f"Cache expired ({cache_age/3600:.1f}h old), clearing")
                    self.cache = {}
                else:
                    logger.info(f"Loaded cache ({cache_age/3600:.1f}h old)")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.cache = {}

    def _save_cache(self):
        """Save cache to file"""
        if not self.enable_cache:
            return

        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache['_metadata'] = {
                'timestamp': time.time(),
                'subdomain': self.subdomain
            }

            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)

            logger.info(f"Cache saved to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make API request with retry logic"""
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                elif method == "POST":
                    response = self.session.post(url, json=data, timeout=30)
                else:
                    logger.error(f"Unsupported method: {method}")
                    return None

                response.raise_for_status()

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after_header = response.headers.get('Retry-After')
                    default_retry_after = BASE_WAIT_TIME * (2 ** attempt)
                    retry_after = default_retry_after

                    if retry_after_header is not None:
                        try:
                            retry_after = max(0, int(retry_after_header))
                        except (TypeError, ValueError):
                            try:
                                retry_at = parsedate_to_datetime(retry_after_header)
                                if retry_at.tzinfo is None:
                                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                                retry_after = max(
                                    0,
                                    int((retry_at - datetime.now(timezone.utc)).total_seconds())
                                )
                            except (TypeError, ValueError, OverflowError):
                                retry_after = default_retry_after

                    logger.warning(f"Rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue

                return response.json()

            except RequestException as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = BASE_WAIT_TIME * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retries exhausted for {endpoint}")
                    return None

        return None

    def fetch_endpoint_data(
        self,
        endpoint: str,
        use_cache: bool = True
    ) -> Optional[List[Dict]]:
        """Fetch data from a Zendesk endpoint"""
        cache_key = f"endpoint_{endpoint}"

        # Check cache
        if use_cache and self.enable_cache and cache_key in self.cache:
            logger.info(f"Using cached data for {endpoint}")
            return self.cache[cache_key]

        logger.info(f"Fetching data from {endpoint}")

        all_items = []
        page = 1

        while True:
            params = {"page": page, "per_page": 100}
            response_data = self._make_request(endpoint, params=params)

            if not response_data:
                break

            # Handle different response structures
            items_key = endpoint.rstrip('s') if endpoint.endswith('s') else endpoint
            items = response_data.get(endpoint, response_data.get(items_key, []))

            if not items:
                break

            all_items.extend(items)

            # Check for pagination
            if not response_data.get('next_page'):
                break

            page += 1
            logger.info(f"Fetched page {page} ({len(all_items)} items so far)")

        logger.info(f"Fetched {len(all_items)} items from {endpoint}")

        # Update cache
        if self.enable_cache:
            self.cache[cache_key] = all_items
            self._save_cache()

        return all_items

    def export_to_json(self, endpoint: str, data: List[Dict]) -> Path:
        """Export endpoint data to JSON file"""
        output_file = self.output_dir / f"{endpoint}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(data)} items to {output_file}")
        return output_file

    def export_to_csv(self, endpoint: str, data: List[Dict]) -> Path:
        """Export endpoint data to CSV file"""
        if not data:
            logger.warning(f"No data to export for {endpoint}")
            return None

        output_file = self.output_dir / f"{endpoint}.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())

        fieldnames = sorted(all_keys)

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Exported {len(data)} items to {output_file}")
        return output_file

    def fetch_all_endpoints(self, export_format: str = "json") -> Dict[str, Any]:
        """Fetch data from all known endpoints"""
        results = {}

        for endpoint in ALL_ENDPOINTS:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing endpoint: {endpoint}")
            logger.info(f"{'='*60}")

            data = self.fetch_endpoint_data(endpoint)

            if data:
                results[endpoint] = {
                    'count': len(data),
                    'data': data
                }

                # Export based on format
                if export_format == "json":
                    self.export_to_json(endpoint, data)
                elif export_format == "csv":
                    self.export_to_csv(endpoint, data)
                elif export_format == "both":
                    self.export_to_json(endpoint, data)
                    self.export_to_csv(endpoint, data)
            else:
                logger.warning(f"No data retrieved for {endpoint}")
                results[endpoint] = {
                    'count': 0,
                    'data': [],
                    'error': 'Failed to fetch data'
                }

        return results

    def generate_summary_report(self, results: Dict[str, Any]) -> Path:
        """Generate summary report of all fetched endpoints"""
        report_file = self.output_dir / "summary_report.txt"

        with open(report_file, 'w') as f:
            f.write("Zendesk Endpoint Manager - Summary Report\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Subdomain: {self.subdomain}\n")
            f.write("="*60 + "\n\n")

            for endpoint, result in results.items():
                status = "✅" if result['count'] > 0 else "❌"
                f.write(f"{status} {endpoint}: {result['count']} items\n")

            f.write("\n" + "="*60 + "\n")
            total_items = sum(r['count'] for r in results.values())
            f.write(f"Total items fetched: {total_items}\n")
            f.write(f"Endpoints processed: {len(results)}\n")

        logger.info(f"Summary report generated: {report_file}")
        return report_file


def main():
    parser = argparse.ArgumentParser(
        description="Zendesk Endpoint Manager for Cognitive Brain"
    )
    parser.add_argument("--subdomain", required=True, help="Zendesk subdomain")
    parser.add_argument("--email", required=True, help="Zendesk email")
    parser.add_argument("--token", required=True, help="Zendesk API token")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="json", help="Export format")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--endpoint", help="Fetch specific endpoint only")

    args = parser.parse_args()

    manager = ZendeskEndpointManager(
        subdomain=args.subdomain,
        email=args.email,
        api_token=args.token,
        output_dir=args.output,
        enable_cache=not args.no_cache
    )

    if args.endpoint:
        # Fetch single endpoint
        data = manager.fetch_endpoint_data(args.endpoint)
        if data:
            if args.format in ["json", "both"]:
                manager.export_to_json(args.endpoint, data)
            if args.format in ["csv", "both"]:
                manager.export_to_csv(args.endpoint, data)
    else:
        # Fetch all endpoints
        results = manager.fetch_all_endpoints(export_format=args.format)
        manager.generate_summary_report(results)

    logger.info("\n✅ Zendesk Endpoint Manager completed successfully")


if __name__ == "__main__":
    main()
