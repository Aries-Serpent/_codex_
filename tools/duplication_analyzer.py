"""
Duplication Analysis and Refactoring Tool

Provides actionable duplicate detection, analysis, and refactoring recommendations.
Addresses the duplication_ratio capability gap by adding functional tools beyond
simple metric calculation.
"""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Duplication thresholds
ACCEPTABLE_DUP_RATIO = 0.10  # 10% duplication is acceptable
WARNING_DUP_RATIO = 0.20  # 20% triggers warnings
CRITICAL_DUP_RATIO = 0.30  # 30% is critical


class DuplicationAnalyzer:
    """Analyze code duplication and provide actionable recommendations"""
    
    def __init__(self, root_path: Path, acceptable_ratio: float = ACCEPTABLE_DUP_RATIO):
        """
        Initialize duplication analyzer
        
        Args:
            root_path: Root directory to analyze
            acceptable_ratio: Acceptable duplication ratio (default: 0.10)
        """
        self.root_path = Path(root_path)
        self.acceptable_ratio = acceptable_ratio
        self.duplicate_groups: Dict[str, List[Path]] = {}
        self.content_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.stats: Dict[str, Any] = {}
    
    def analyze(self, extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive duplication analysis
        
        Args:
            extensions: File extensions to analyze (default: ['.py', '.md', '.yaml', '.json'])
            
        Returns:
            Analysis report with duplicates, recommendations, and metrics
        """
        if extensions is None:
            extensions = ['.py', '.md', '.yaml', '.yml', '.json', '.txt']
        
        # Find all relevant files
        files = []
        for ext in extensions:
            files.extend(self.root_path.rglob(f'*{ext}'))
        
        # Analyze by filename stems
        stem_groups = defaultdict(list)
        for filepath in files:
            if filepath.is_file():
                stem = filepath.stem.lower()
                stem_groups[stem].append(filepath)
        
        # Identify duplicates by stem
        self.duplicate_groups = {
            stem: paths for stem, paths in stem_groups.items() if len(paths) > 1
        }
        
        # Analyze by content hash
        for filepath in files:
            if filepath.is_file():
                try:
                    content_hash = self._hash_file(filepath)
                    self.content_hashes[content_hash].append(filepath)
                except Exception:
                    continue
        
        # Calculate metrics
        total_files = len(files)
        duplicate_count = sum(max(len(paths) - 1, 0) for paths in stem_groups.values())
        dup_ratio = duplicate_count / max(total_files, 1)
        
        # Build statistics
        self.stats = {
            "total_files": total_files,
            "duplicate_count": duplicate_count,
            "duplication_ratio": dup_ratio,
            "duplicate_groups_count": len(self.duplicate_groups),
            "content_duplicate_groups": len([h for h, paths in self.content_hashes.items() if len(paths) > 1]),
            "severity": self._assess_severity(dup_ratio),
        }
        
        return {
            "stats": self.stats,
            "duplicate_groups": self._format_duplicate_groups(),
            "content_duplicates": self._format_content_duplicates(),
            "recommendations": self._generate_recommendations(),
        }
    
    def _hash_file(self, filepath: Path) -> str:
        """Compute SHA-256 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _assess_severity(self, ratio: float) -> str:
        """Assess duplication severity"""
        if ratio < self.acceptable_ratio:
            return "acceptable"
        elif ratio < WARNING_DUP_RATIO:
            return "warning"
        elif ratio < CRITICAL_DUP_RATIO:
            return "high"
        else:
            return "critical"
    
    def _format_duplicate_groups(self) -> List[Dict[str, Any]]:
        """Format duplicate groups for reporting"""
        groups = []
        for stem, paths in sorted(self.duplicate_groups.items(), key=lambda x: -len(x[1]))[:20]:
            groups.append({
                "stem": stem,
                "count": len(paths),
                "paths": [str(p.relative_to(self.root_path)) for p in paths],
                "recommendation": self._recommend_for_stem_duplicates(stem, paths)
            })
        return groups
    
    def _format_content_duplicates(self) -> List[Dict[str, Any]]:
        """Format content-based duplicates"""
        duplicates = []
        for content_hash, paths in self.content_hashes.items():
            if len(paths) > 1:
                duplicates.append({
                    "hash": content_hash[:16],
                    "count": len(paths),
                    "paths": [str(p.relative_to(self.root_path)) for p in paths],
                    "recommendation": "Identical content detected. Consider consolidation or deduplication."
                })
        return sorted(duplicates, key=lambda x: -x["count"])[:10]
    
    def _recommend_for_stem_duplicates(self, stem: str, paths: List[Path]) -> str:
        """Generate recommendation for stem duplicates"""
        # Check if they're in different directories
        dirs = set(p.parent for p in paths)
        
        if len(dirs) == len(paths):
            return "Files in different directories. Consider if they serve different purposes or can be merged."
        else:
            return "Multiple files with same name in same/nearby directories. High priority for review and consolidation."
    
    def _generate_recommendations(self) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        ratio = self.stats["duplication_ratio"]
        
        if ratio < self.acceptable_ratio:
            recommendations.append(f"✅ Duplication ratio ({ratio:.2%}) is within acceptable limits.")
        elif ratio < WARNING_DUP_RATIO:
            recommendations.append(f"⚠️ Duplication ratio ({ratio:.2%}) is elevated. Review duplicate groups.")
        else:
            recommendations.append(f"🔴 Duplication ratio ({ratio:.2%}) is high. Immediate action recommended.")
        
        if self.duplicate_groups:
            recommendations.append(f"Found {len(self.duplicate_groups)} groups of files with duplicate names.")
            recommendations.append("Review top duplicate groups and consider:")
            recommendations.append("  - Consolidating similar functionality")
            recommendations.append("  - Renaming files to reflect their specific purpose")
            recommendations.append("  - Removing obsolete duplicates")
        
        content_dups = len([h for h, paths in self.content_hashes.items() if len(paths) > 1])
        if content_dups > 0:
            recommendations.append(f"Found {content_dups} groups of files with identical content.")
            recommendations.append("  - Remove exact duplicates")
            recommendations.append("  - Use symbolic links or imports if copies are needed")
        
        return recommendations
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate markdown report
        
        Args:
            output_path: Optional path to save report
            
        Returns:
            Markdown formatted report
        """
        analysis = self.analyze()
        
        report = f"""# Duplication Analysis Report

## Summary

| Metric | Value |
|--------|------:|
| Total Files | {analysis['stats']['total_files']} |
| Duplicate Count | {analysis['stats']['duplicate_count']} |
| Duplication Ratio | {analysis['stats']['duplication_ratio']:.2%} |
| Severity | {analysis['stats']['severity'].upper()} |
| Duplicate Groups | {analysis['stats']['duplicate_groups_count']} |
| Content Duplicates | {analysis['stats']['content_duplicate_groups']} |

## Recommendations

"""
        for rec in analysis['recommendations']:
            report += f"- {rec}\n"
        
        report += "\n## Top Duplicate Groups (by filename stem)\n\n"
        for group in analysis['duplicate_groups'][:10]:
            report += f"### `{group['stem']}` ({group['count']} files)\n\n"
            report += f"**Recommendation**: {group['recommendation']}\n\n"
            report += "Files:\n"
            for path in group['paths']:
                report += f"- `{path}`\n"
            report += "\n"
        
        if analysis['content_duplicates']:
            report += "\n## Content-Based Duplicates (identical files)\n\n"
            for dup in analysis['content_duplicates'][:5]:
                report += f"### Hash: `{dup['hash']}...` ({dup['count']} files)\n\n"
                for path in dup['paths']:
                    report += f"- `{path}`\n"
                report += f"\n**Action**: {dup['recommendation']}\n\n"
        
        if output_path:
            output_path.write_text(report, encoding='utf-8')
        
        return report
    
    def find_refactoring_candidates(self, min_duplicates: int = 3) -> List[Dict[str, Any]]:
        """
        Find files that are good candidates for refactoring
        
        Args:
            min_duplicates: Minimum number of duplicates to consider
            
        Returns:
            List of refactoring candidates with priority
        """
        candidates = []
        
        for stem, paths in self.duplicate_groups.items():
            if len(paths) >= min_duplicates:
                # Check for Python files (higher priority)
                py_files = [p for p in paths if p.suffix == '.py']
                
                priority = "high" if len(py_files) >= 2 else "medium"
                
                candidates.append({
                    "stem": stem,
                    "count": len(paths),
                    "priority": priority,
                    "files": [str(p.relative_to(self.root_path)) for p in paths],
                    "suggestion": self._suggest_refactoring(stem, paths)
                })
        
        return sorted(candidates, key=lambda x: (-len(x["files"]), x["priority"]))
    
    def _suggest_refactoring(self, stem: str, paths: List[Path]) -> str:
        """Suggest refactoring approach"""
        # Check file types
        extensions = set(p.suffix for p in paths)
        
        if '.py' in extensions:
            return "Consider creating a shared module or base class to eliminate duplication."
        elif '.md' in extensions:
            return "Consider consolidating documentation or using includes/links."
        elif '.yaml' in extensions or '.yml' in extensions:
            return "Consider using YAML anchors/aliases or shared configuration files."
        else:
            return "Review and consolidate if files serve the same purpose."


def cli_main():
    """Command-line interface for duplication analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze code duplication")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory to analyze")
    parser.add_argument("--output", type=Path, help="Output report path")
    parser.add_argument("--threshold", type=float, default=ACCEPTABLE_DUP_RATIO, help="Acceptable duplication ratio")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    
    args = parser.parse_args()
    
    analyzer = DuplicationAnalyzer(args.root, acceptable_ratio=args.threshold)
    
    if args.json:
        analysis = analyzer.analyze()
        output = json.dumps(analysis, indent=2)
        if args.output:
            args.output.write_text(output, encoding='utf-8')
        else:
            print(output)
    else:
        report = analyzer.generate_report(args.output)
        if not args.output:
            print(report)
    
    # Exit with error code if duplication is above threshold
    if analyzer.stats.get("duplication_ratio", 0) > args.threshold:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(cli_main())
