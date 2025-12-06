"""Stub cleanup utilities for identifying and resolving NotImplementedError and TODO items.

This module helps track and resolve stubs, TODOs, and FIXMEs in the codebase.
"""
from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

__all__ = ["StubInfo", "StubAnalyzer", "find_stubs", "prioritize_stubs"]


@dataclass
class StubInfo:
    """Information about a stub/TODO in the codebase.
    
    Attributes:
        file_path: Path to file containing stub
        line_number: Line number
        stub_type: Type of stub (NotImplementedError, TODO, FIXME)
        message: Message/description
        priority: Priority level (P0, P1, P2)
        context: Surrounding code context
    """
    file_path: Path
    line_number: int
    stub_type: str
    message: str
    priority: str = "P2"
    context: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.priority} {self.file_path}:{self.line_number} [{self.stub_type}] {self.message}"


class StubAnalyzer:
    """Analyzer for finding and categorizing stubs in code."""
    
    def __init__(self, source_dirs: Optional[List[Path]] = None):
        """Initialize stub analyzer.
        
        Args:
            source_dirs: List of source directories to analyze
        """
        if source_dirs is None:
            source_dirs = [Path("src"), Path("training")]
        
        self.source_dirs = [Path(d) for d in source_dirs]
        self.stubs: List[StubInfo] = []
    
    def analyze(self) -> List[StubInfo]:
        """Analyze source directories for stubs.
        
        Returns:
            List of StubInfo objects
        """
        self.stubs = []
        
        for source_dir in self.source_dirs:
            if not source_dir.exists():
                continue
            
            # Find all Python files
            for py_file in source_dir.rglob("*.py"):
                self._analyze_file(py_file)
        
        return self.stubs
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single file for stubs.
        
        Args:
            file_path: Path to Python file
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Simple text-based analysis for TODOs/FIXMEs
            for i, line in enumerate(lines, start=1):
                line_lower = line.lower()
                
                # Check for TODO
                if "todo" in line_lower and "#" in line:
                    priority = self._determine_priority(line)
                    message = line.split("#", 1)[1].strip()
                    
                    self.stubs.append(StubInfo(
                        file_path=file_path,
                        line_number=i,
                        stub_type="TODO",
                        message=message,
                        priority=priority,
                        context=line.strip()
                    ))
                
                # Check for FIXME
                if "fixme" in line_lower and "#" in line:
                    priority = self._determine_priority(line)
                    message = line.split("#", 1)[1].strip()
                    
                    self.stubs.append(StubInfo(
                        file_path=file_path,
                        line_number=i,
                        stub_type="FIXME",
                        message=message,
                        priority=priority,
                        context=line.strip()
                    ))
                
                # Check for NotImplementedError
                if "notimplementederror" in line_lower:
                    priority = "P0"  # NotImplementedError is always high priority
                    
                    # Try to extract message
                    if "(" in line and ")" in line:
                        message_part = line.split("(", 1)[1].rsplit(")", 1)[0]
                        message = message_part.strip('"\'')
                    else:
                        message = "NotImplementedError"
                    
                    self.stubs.append(StubInfo(
                        file_path=file_path,
                        line_number=i,
                        stub_type="NotImplementedError",
                        message=message,
                        priority=priority,
                        context=line.strip()
                    ))
        
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
    
    def _determine_priority(self, line: str) -> str:
        """Determine priority from line content.
        
        Args:
            line: Source code line
            
        Returns:
            Priority level (P0, P1, P2)
        """
        line_upper = line.upper()
        
        if "P0" in line_upper or "CRITICAL" in line_upper or "BLOCKING" in line_upper:
            return "P0"
        elif "P1" in line_upper or "HIGH" in line_upper or "IMPORTANT" in line_upper:
            return "P1"
        else:
            return "P2"
    
    def get_by_priority(self, priority: str) -> List[StubInfo]:
        """Get stubs by priority level.
        
        Args:
            priority: Priority level (P0, P1, P2)
            
        Returns:
            List of stubs with specified priority
        """
        return [stub for stub in self.stubs if stub.priority == priority]
    
    def get_by_type(self, stub_type: str) -> List[StubInfo]:
        """Get stubs by type.
        
        Args:
            stub_type: Type of stub (NotImplementedError, TODO, FIXME)
            
        Returns:
            List of stubs with specified type
        """
        return [stub for stub in self.stubs if stub.stub_type == stub_type]
    
    def get_summary(self) -> dict:
        """Get summary of stub analysis.
        
        Returns:
            Summary dict with counts by priority and type
        """
        summary = {
            "total": len(self.stubs),
            "by_priority": {
                "P0": len(self.get_by_priority("P0")),
                "P1": len(self.get_by_priority("P1")),
                "P2": len(self.get_by_priority("P2"))
            },
            "by_type": {
                "NotImplementedError": len(self.get_by_type("NotImplementedError")),
                "TODO": len(self.get_by_type("TODO")),
                "FIXME": len(self.get_by_type("FIXME"))
            }
        }
        return summary


def find_stubs(source_dirs: Optional[List[Path]] = None) -> List[StubInfo]:
    """Find all stubs in source directories (convenience function).
    
    Args:
        source_dirs: List of source directories to analyze
        
    Returns:
        List of StubInfo objects
    """
    analyzer = StubAnalyzer(source_dirs=source_dirs)
    return analyzer.analyze()


def prioritize_stubs(stubs: List[StubInfo]) -> List[StubInfo]:
    """Sort stubs by priority (P0 first, then P1, then P2).
    
    Args:
        stubs: List of StubInfo objects
        
    Returns:
        Sorted list with P0 first
    """
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return sorted(stubs, key=lambda s: (priority_order.get(s.priority, 3), str(s.file_path), s.line_number))


def generate_stub_report(output_path: Path | str, source_dirs: Optional[List[Path]] = None):
    """Generate stub analysis report.
    
    Args:
        output_path: Path where report will be saved
        source_dirs: List of source directories to analyze
    """
    analyzer = StubAnalyzer(source_dirs=source_dirs)
    stubs = analyzer.analyze()
    sorted_stubs = prioritize_stubs(stubs)
    
    summary = analyzer.get_summary()
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Stub Analysis Report\n\n")
        f.write(f"**Total Stubs**: {summary['total']}\n\n")
        
        f.write("## Summary by Priority\n\n")
        for priority in ["P0", "P1", "P2"]:
            count = summary["by_priority"][priority]
            f.write(f"- **{priority}**: {count}\n")
        
        f.write("\n## Summary by Type\n\n")
        for stub_type, count in summary["by_type"].items():
            f.write(f"- **{stub_type}**: {count}\n")
        
        f.write("\n## Detailed List\n\n")
        
        for priority in ["P0", "P1", "P2"]:
            priority_stubs = [s for s in sorted_stubs if s.priority == priority]
            if not priority_stubs:
                continue
            
            f.write(f"\n### {priority} Priority ({len(priority_stubs)} items)\n\n")
            
            for stub in priority_stubs:
                f.write(f"**{stub.file_path}:{stub.line_number}** [{stub.stub_type}]\n")
                f.write(f"- Message: {stub.message}\n")
                if stub.context:
                    f.write(f"- Context: `{stub.context}`\n")
                f.write("\n")
    
    logger.info(f"Stub report generated: {output_path}")
    print(f"\n✓ Stub analysis complete:")
    print(f"  Total stubs: {summary['total']}")
    print(f"  P0: {summary['by_priority']['P0']}")
    print(f"  P1: {summary['by_priority']['P1']}")
    print(f"  P2: {summary['by_priority']['P2']}")
    print(f"  Report: {output_path}")
