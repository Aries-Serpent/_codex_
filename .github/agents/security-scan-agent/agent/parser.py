"""
SARIF parser module for security scan results.

Parses SARIF JSON format and extracts security findings with locations.

#AFTERMATH_PATTERN_IDENTIFIED - SARIF standardization for cross-tool compatibility
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Location:
    """Code location for a finding."""
    
    file_path: str
    start_line: int
    end_line: int
    start_column: int = 1
    end_column: int = 1
    region_snippet: str = ""


@dataclass
class Finding:
    """A security finding from SARIF."""
    
    rule_id: str
    message: str
    level: str  # "error", "warning", "note"
    locations: list[Location] = field(default_factory=list)
    tool: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedSARIF:
    """Parsed SARIF results."""
    
    tool_name: str
    tool_version: str
    findings: list[Finding]
    total_count: int = 0


class SARIFParser:
    """
    Parser for SARIF (Static Analysis Results Interchange Format).
    
    Extracts findings with locations from SARIF JSON output.
    
    #AFTERMATH_QUALITY_CHECK - Defensive parsing with validation
    """
    
    def parse_file(self, sarif_path: Path) -> ParsedSARIF:
        """
        Parse SARIF file.
        
        Args:
            sarif_path: Path to SARIF JSON file
            
        Returns:
            Parsed SARIF results
            
        Raises:
            FileNotFoundError: If SARIF file doesn't exist
            json.JSONDecodeError: If SARIF is invalid JSON
        """
        if not sarif_path.exists():
            raise FileNotFoundError(f"SARIF file not found: {sarif_path}")
        
        logger.info("Parsing SARIF file: %s", sarif_path)
        
        with open(sarif_path) as f:
            sarif_data = json.load(f)
        
        return self.parse_sarif(sarif_data)
    
    def parse_sarif(self, sarif_data: dict[str, Any]) -> ParsedSARIF:
        """
        Parse SARIF data structure.
        
        Args:
            sarif_data: SARIF JSON data
            
        Returns:
            Parsed SARIF results
        """
        # Validate SARIF version
        version = sarif_data.get("version", "")
        if not version.startswith("2.1"):
            logger.warning("Unsupported SARIF version: %s", version)
        
        # Extract tool info and findings from all runs
        all_findings: list[Finding] = []
        tool_name = "unknown"
        tool_version = "unknown"
        
        for run in sarif_data.get("runs", []):
            # Extract tool info
            tool_info = run.get("tool", {}).get("driver", {})
            tool_name = tool_info.get("name", tool_name)
            tool_version = tool_info.get("version", tool_version)
            
            # Parse results
            for result in run.get("results", []):
                finding = self._parse_result(result, tool_name)
                all_findings.append(finding)
        
        logger.info(
            "Parsed SARIF: tool=%s, findings=%d",
            tool_name,
            len(all_findings)
        )
        
        return ParsedSARIF(
            tool_name=tool_name,
            tool_version=tool_version,
            findings=all_findings,
            total_count=len(all_findings)
        )
    
    def _parse_result(self, result: dict[str, Any], tool: str) -> Finding:
        """
        Parse a single SARIF result.
        
        Args:
            result: SARIF result object
            tool: Tool name
            
        Returns:
            Finding object
        """
        # Extract rule ID
        rule_id = result.get("ruleId", "unknown")
        
        # Extract message
        message_obj = result.get("message", {})
        message = message_obj.get("text", "No message provided")
        
        # Extract level
        level = result.get("level", "warning")
        
        # Extract locations
        locations = []
        for loc in result.get("locations", []):
            physical_loc = loc.get("physicalLocation", {})
            artifact_loc = physical_loc.get("artifactLocation", {})
            region = physical_loc.get("region", {})
            
            file_path = artifact_loc.get("uri", "unknown")
            start_line = region.get("startLine", 1)
            end_line = region.get("endLine", start_line)
            start_column = region.get("startColumn", 1)
            end_column = region.get("endColumn", 1)
            snippet = region.get("snippet", {}).get("text", "")
            
            locations.append(Location(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                start_column=start_column,
                end_column=end_column,
                region_snippet=snippet
            ))
        
        # Extract metadata
        metadata = {
            "ruleIndex": result.get("ruleIndex"),
            "properties": result.get("properties", {}),
        }
        
        return Finding(
            rule_id=rule_id,
            message=message,
            level=level,
            locations=locations,
            tool=tool,
            metadata=metadata
        )
    
    def findings_by_severity(
        self,
        findings: list[Finding]
    ) -> dict[str, list[Finding]]:
        """
        Group findings by severity level.
        
        Args:
            findings: List of findings
            
        Returns:
            Dictionary mapping level to findings
        """
        grouped: dict[str, list[Finding]] = {
            "error": [],
            "warning": [],
            "note": [],
        }
        
        for finding in findings:
            level = finding.level
            if level in grouped:
                grouped[level].append(finding)
            else:
                grouped.setdefault(level, []).append(finding)
        
        return grouped
    
    def findings_by_file(
        self,
        findings: list[Finding]
    ) -> dict[str, list[Finding]]:
        """
        Group findings by file path.
        
        Args:
            findings: List of findings
            
        Returns:
            Dictionary mapping file path to findings
        """
        grouped: dict[str, list[Finding]] = {}
        
        for finding in findings:
            for location in finding.locations:
                file_path = location.file_path
                grouped.setdefault(file_path, []).append(finding)
        
        return grouped


# #AFTERMATH_METRIC - SARIF parser with location extraction
# #AFTERMATH_QUALITY_CHECK - Defensive parsing with fallback values
