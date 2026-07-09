"""Training data integration for synchronized SaaS knowledge.

This module provides utilities to integrate synchronized Zendesk and Dynamics 365
knowledge into the training pipeline, enabling the Agent to fine-tune on current
SaaS documentation.

Phase 4: MLOps Automation - Training & Verification Loop
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SaaSKnowledgeLoader:
    """Load synchronized SaaS knowledge for training.

    This class integrates with:
    - src/services/crawler/zendesk_sync.py (synchronized docs)
    - src/codex/dynamics/model/sla.py (policy objects)
    - data/zendesk_api_index.json (tracking cache)
    """

    def __init__(
        self,
        *,
        zendesk_docs_root: Path | None = None,
        zendesk_index_path: Path | None = None,
        d365_policies_path: Path | None = None,
        repo_root: Path | None = None,
    ) -> None:
        """Initialize knowledge loader.

        Args:
            zendesk_docs_root: Root directory for Zendesk docs
            zendesk_index_path: Path to zendesk_api_index.json
            d365_policies_path: Path to D365 SLA policies JSON
            repo_root: Repository root (auto-detected if None)
        """
        if repo_root is None:
            # Auto-detect from this file's location
            repo_root = Path(__file__).resolve().parents[3]

        self.repo_root = Path(repo_root)

        self.zendesk_docs_root = (
            Path(zendesk_docs_root)
            if zendesk_docs_root
            else self.repo_root / "docs" / "vendors" / "zendesk"
        )

        self.zendesk_index_path = (
            Path(zendesk_index_path)
            if zendesk_index_path
            else self.repo_root / "data" / "zendesk_api_index.json"
        )

        self.d365_policies_path = (
            Path(d365_policies_path)
            if d365_policies_path
            else self.repo_root / "configs" / "deployment" / "d365" / "sla_policies.json"
        )

    def get_latest_zendesk_sync(self) -> Path | None:
        """Get the most recent Zendesk documentation sync directory.

        Returns:
            Path to latest sync directory, or None if no syncs found
        """
        if not self.zendesk_docs_root.exists():
            logger.warning(f"Zendesk docs root not found: {self.zendesk_docs_root}")
            return None

        # Find dated directories (YYYY-MM-DD format)
        sync_dirs = [
            d
            for d in self.zendesk_docs_root.iterdir()
            if d.is_dir() and d.name.replace("-", "").isdigit()
        ]

        if not sync_dirs:
            logger.warning("No Zendesk sync directories found")
            return None

        # Sort by name (ISO date format sorts correctly)
        latest = sorted(sync_dirs, reverse=True)[0]
        logger.info(f"Latest Zendesk sync: {latest}")
        return latest

    def load_zendesk_index(self) -> dict[str, Any]:
        """Load Zendesk API index with metadata.

        Returns:
            Dictionary with sync metadata and article cache
        """
        if not self.zendesk_index_path.exists():
            logger.warning(f"Zendesk index not found: {self.zendesk_index_path}")
            return {}

        try:
            with self.zendesk_index_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded Zendesk index with {len(data.get('articles', {}))} articles")
            return data
        except (json.JSONDecodeError, OSError) as e:
            type(e).__name__
            logger.error("Failed to load Zendesk index: <ERROR_TYPE>")
            return {}

    def load_d365_policies(self) -> dict[str, Any]:
        """Load Dynamics 365 SLA policies.

        Returns:
            SLA policy registry data
        """
        if not self.d365_policies_path.exists():
            logger.warning(f"D365 policies not found: {self.d365_policies_path}")
            return {}

        try:
            with self.d365_policies_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data.get('policies', []))} D365 SLA policies")
            return data
        except (json.JSONDecodeError, OSError) as e:
            type(e).__name__
            logger.error("Failed to load D365 policies: <ERROR_TYPE>")
            return {}

    def collect_training_documents(
        self,
        *,
        include_zendesk: bool = True,
        include_d365: bool = True,
    ) -> list[dict[str, Any]]:
        """Collect all training documents from synchronized sources.

        Args:
            include_zendesk: Include Zendesk documentation
            include_d365: Include Dynamics 365 policies

        Returns:
            List of training document dictionaries with metadata
        """
        documents = []

        if include_zendesk:
            latest_sync = self.get_latest_zendesk_sync()
            if latest_sync:
                # Collect HTML files
                html_files = list(latest_sync.rglob("*.html"))
                logger.info(f"Found {len(html_files)} Zendesk documents")

                for html_file in html_files:
                    # Extract section/bucket from path
                    rel_path = html_file.relative_to(latest_sync)
                    parts = rel_path.parts

                    documents.append(
                        {
                            "source": "zendesk",
                            "path": str(html_file),
                            "section": parts[0] if len(parts) > 0 else "unknown",
                            "bucket": parts[1] if len(parts) > 1 else "unknown",
                            "sync_date": latest_sync.name,
                            "type": "documentation",
                        }
                    )

        if include_d365:
            policies = self.load_d365_policies()
            policy_list = policies.get("policies", [])
            logger.info(f"Found {len(policy_list)} D365 policies")

            for policy in policy_list:
                documents.append(
                    {
                        "source": "dynamics365",
                        "name": policy.get("name", "unknown"),
                        "metric": policy.get("metric", "unknown"),
                        "content": json.dumps(policy),
                        "type": "policy",
                        "version": policy.get("version", "1.0.0"),
                    }
                )

        logger.info(f"Collected {len(documents)} training documents")
        return documents

    def prepare_training_dataset(
        self,
        output_path: Path,
        *,
        include_zendesk: bool = True,
        include_d365: bool = True,
    ) -> Path:
        """Prepare a training dataset from synchronized sources.

        Args:
            output_path: Path for output JSONL file
            include_zendesk: Include Zendesk documentation
            include_d365: Include Dynamics 365 policies

        Returns:
            Path to created dataset file
        """
        documents = self.collect_training_documents(
            include_zendesk=include_zendesk,
            include_d365=include_d365,
        )

        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSONL
        with output_path.open("w", encoding="utf-8") as f:
            for doc in documents:
                f.write(json.dumps(doc) + "\n")

        logger.info(f"Created training dataset: {output_path}")
        logger.info(f"  - {len(documents)} documents")

        # Create metadata file
        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "document_count": len(documents),
            "sources": {
                "zendesk": include_zendesk,
                "dynamics365": include_d365,
            },
            "zendesk_sync": str(self.get_latest_zendesk_sync()) if include_zendesk else None,
        }

        metadata_path = output_path.with_suffix(".meta.json")
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Created metadata: {metadata_path}")

        return output_path


def create_saas_training_dataset(
    output_path: str | Path = "data/processed/saas_knowledge.jsonl",
    *,
    include_zendesk: bool = True,
    include_d365: bool = True,
) -> Path:
    """Convenience function to create SaaS training dataset.

    Args:
        output_path: Path for output dataset
        include_zendesk: Include Zendesk documentation
        include_d365: Include Dynamics 365 policies

    Returns:
        Path to created dataset
    """
    loader = SaaSKnowledgeLoader()
    return loader.prepare_training_dataset(
        Path(output_path),
        include_zendesk=include_zendesk,
        include_d365=include_d365,
    )


__all__ = [
    "SaaSKnowledgeLoader",
    "create_saas_training_dataset",
]
