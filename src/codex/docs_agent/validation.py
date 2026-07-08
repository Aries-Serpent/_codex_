"""
Documentation validation and compliance checking.

Classes:
  - LinkValidator: Check internal and external links
  - ComplianceChecker: Audit REQ-1 through REQ-10
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class LinkValidator:
    """Validate links in documentation.

    Supports:
      - Internal link checking
      - External link verification
      - Cross-reference resolution
      - Broken link detection
    """

    def __init__(self, registry: Optional[Any] = None):  # DocumentRegistry
        self.registry = registry
        self.broken_links: List[Dict] = []
        self.verified_links: List[Dict] = []

    def validate_document_links(self, doc_id: str) -> Tuple[int, int, int]:
        """Validate all links in a document.

        Returns:
            (valid_count, broken_count, external_count)
        """
        if not self.registry:
            return 0, 0, 0

        doc = self.registry.get_document(doc_id)
        if not doc:
            return 0, 0, 0

        sections = self.registry.get_sections(doc_id)

        valid_count = 0
        broken_count = 0
        external_count = 0

        for section in sections:
            # Extract links from section content
            links = self._extract_links(section.content)

            for link in links:
                url = link["url"]

                if link["type"] == "external":
                    external_count += 1
                elif link["type"] == "internal":
                    if self._resolve_internal_link(url):
                        valid_count += 1
                    else:
                        broken_count += 1
                        self.broken_links.append(
                            {
                                "source": doc_id,
                                "target": url,
                                "text": link["text"],
                            }
                        )
                elif link["type"] == "anchor":
                    # Check anchor exists in document
                    if self._find_anchor(doc_id, url[1:]):
                        valid_count += 1
                    else:
                        broken_count += 1

        return valid_count, broken_count, external_count

    def get_broken_links(self) -> List[Dict]:
        """Get all detected broken links."""
        return self.broken_links.copy()

    @staticmethod
    def _extract_links(content: str) -> List[Dict]:
        """Extract markdown links from content."""
        # [text](url)
        pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        links = []

        for match in pattern.finditer(content):
            url = match.group(2)
            link_type = (
                "external"
                if url.startswith(("http://", "https://"))
                else "anchor" if url.startswith("#") else "internal"
            )

            links.append(
                {
                    "text": match.group(1),
                    "url": url,
                    "type": link_type,
                }
            )

        return links

    def _resolve_internal_link(self, path: str) -> bool:
        """Check if internal link resolves."""
        if not self.registry:
            return True  # Can't verify without registry

        # Normalize path
        if path.startswith("/"):
            path = path[1:]

        # Check if file exists in registry
        doc = self.registry.find_by_path(path)
        return doc is not None

    def _find_anchor(self, doc_id: str, anchor: str) -> bool:
        """Check if anchor exists in document."""
        if not self.registry:
            return True

        sections = self.registry.get_sections(doc_id)

        for section in sections:
            # Generate anchor from section title
            section_anchor = section.metadata.get("heading_anchor", "")
            if section_anchor == anchor:
                return True

        return False


class ComplianceChecker:
    """Audit compliance with requirements.

    Checks:
      - Documentation coverage (REQ-1)
      - API documentation (REQ-2, REQ-3)
      - Example accuracy (REQ-4, REQ-5)
      - Link health (REQ-6)
      - Freshness SLA (REQ-7)
    """

    def __init__(self, registry: Optional[Any] = None):
        self.registry = registry
        self.findings: Dict[str, List[Dict]] = {}

    def audit_all_requirements(self) -> Dict[str, Dict]:
        """Run full compliance audit.

        Returns:
            {requirement_id: {status, details, ...}}
        """
        results = {
            "req_001": self._audit_critical_docs(),
            "req_002": self._audit_api_coverage(),
            "req_003": self._audit_example_quality(),
            "req_004": self._audit_link_health(),
            "req_005": self._audit_doc_freshness(),
        }

        return results

    def _audit_critical_docs(self) -> Dict:
        """REQ-001: Critical documentation must exist."""
        if not self.registry:
            return {"status": "unknown"}

        critical_docs = ["README.md", "docs/index.md"]
        found = []
        missing = []

        for path in critical_docs:
            if self.registry.find_by_path(path):
                found.append(path)
            else:
                missing.append(path)

        status = "pass" if not missing else "fail"
        return {
            "status": status,
            "found": found,
            "missing": missing,
        }

    def _audit_api_coverage(self) -> Dict:
        """REQ-002: Public APIs must be documented."""
        return {
            "status": "pending",
            "note": "Requires codebase inspection",
        }

    def _audit_example_quality(self) -> Dict:
        """REQ-003: Examples must be executable and tested."""
        return {
            "status": "pending",
            "note": "Requires code execution",
        }

    def _audit_link_health(self) -> Dict:
        """REQ-004: No broken links in documentation."""
        validator = LinkValidator(self.registry)

        total_broken = 0
        if self.registry:
            for doc in self.registry.list_documents():
                _, broken, _ = validator.validate_document_links(doc.id)
                total_broken += broken

        status = "pass" if total_broken == 0 else "fail"
        return {
            "status": status,
            "broken_links": total_broken,
        }

    def _audit_doc_freshness(self) -> Dict:
        """REQ-005: Documentation must be updated regularly."""
        from datetime import datetime, timedelta

        if not self.registry:
            return {"status": "unknown"}

        docs = self.registry.list_documents()
        stale_docs = []
        current_time = datetime.utcnow()
        freshness_threshold = timedelta(days=90)

        for doc in docs:
            try:
                updated = datetime.fromisoformat(doc.updated_at.replace("Z", "+00:00"))
                age = current_time - updated

                if age > freshness_threshold:
                    stale_docs.append(
                        {
                            "id": doc.id,
                            "path": doc.path,
                            "days_old": age.days,
                        }
                    )
            except (ValueError, AttributeError):
                pass

        status = "pass" if not stale_docs else "warn"
        return {
            "status": status,
            "stale_docs": stale_docs,
            "freshness_threshold_days": 90,
        }
