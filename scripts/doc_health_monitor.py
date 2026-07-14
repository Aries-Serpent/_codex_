#!/usr/bin/env python3
"""
Documentation Freshness & Health Monitoring System
Automated daily validation and reporting for documentation ecosystem

Phase 4D Planset 006 - Deliverable
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import subprocess

class DocHealthMonitor:
    """Monitor documentation health, freshness, and quality"""
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.reports = {}
        self.issues = defaultdict(list)
        self.metrics = {}
        self.timestamp = datetime.now()
        
    def scan_all_files(self) -> Dict[str, dict]:
        """Scan all markdown files and extract metadata"""
        files = {}
        for md_file in self.docs_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.docs_root))
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                stat = os.stat(md_file)
                
                files[rel_path] = {
                    'path': str(md_file),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'lines': len(content.split('\n')),
                    'content': content,
                    'links': self._extract_links(content),
                    'has_headers': bool(re.search(r'^#+', content, re.MULTILINE)),
                }
            except Exception as e:
                self.issues['scan_errors'].append(f"{rel_path}: {e}")
        
        return files
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract all markdown links from content"""
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = []
        for match in re.finditer(pattern, content):
            links.append(match.group(2))
        return links
    
    def validate_links(self, files: Dict[str, dict]) -> Dict[str, list]:
        """Validate all internal links"""
        issues = defaultdict(list)
        file_paths = set(files.keys())
        
        for filepath, data in files.items():
            for link in data['links']:
                # Skip external links and anchors
                if '://' in link or link.startswith('#'):
                    continue
                
                link_clean = link.split('#')[0]
                if link_clean and not link_clean.startswith('http'):
                    # Check if link target exists
                    target = link_clean if link_clean.endswith('.md') else link_clean + '.md'
                    
                    if target not in file_paths and not self._check_github_link(link_clean):
                        issues['broken_links'].append({
                            'file': filepath,
                            'link': link,
                            'target': target
                        })
        
        return dict(issues)
    
    def _check_github_link(self, link: str) -> bool:
        """Check if link is a valid GitHub reference"""
        return link.startswith('https://github.com/Aries-Serpent/_codex_/')
    
    def check_freshness(self, files: Dict[str, dict], 
                       stale_threshold_days: int = 90) -> Dict[str, list]:
        """Check content freshness"""
        issues = defaultdict(list)
        cutoff_date = datetime.now() - timedelta(days=stale_threshold_days)
        
        for filepath, data in files.items():
            if data['modified'] < cutoff_date:
                age_days = (datetime.now() - data['modified']).days
                issues['stale_content'].append({
                    'file': filepath,
                    'last_modified': data['modified'].isoformat(),
                    'age_days': age_days
                })
        
        return dict(issues)
    
    def detect_orphaned_pages(self, mkdocs_path: str = "mkdocs.yml") -> Set[str]:
        """Detect pages not in mkdocs.yml navigation"""
        import yaml
        
        with open(mkdocs_path) as f:
            content = yaml.safe_load(f)
        
        nav_files = self._collect_nav_files(content.get('nav', []))
        
        all_files = set()
        for md_file in self.docs_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.docs_root))
            if rel_path != "index.md":
                all_files.add(rel_path)
        
        orphaned = all_files - nav_files
        return orphaned
    
    def _collect_nav_files(self, nav_list: list) -> set:
        """Collect all files referenced in nav structure"""
        files = set()
        if not nav_list:
            return files
        
        for item in nav_list:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and value.endswith('.md'):
                        files.add(value)
                    elif isinstance(value, list):
                        files.update(self._collect_nav_files(value))
        
        return files
    
    def check_structure_compliance(self, files: Dict[str, dict]) -> Dict[str, list]:
        """Check documentation structure compliance"""
        issues = defaultdict(list)
        
        for filepath, data in files.items():
            # Check for headers
            if not data['has_headers']:
                issues['missing_headers'].append({
                    'file': filepath,
                    'reason': 'No markdown headers found'
                })
            
            # Check for minimum content
            if data['lines'] < 3:
                issues['minimal_content'].append({
                    'file': filepath,
                    'lines': data['lines']
                })
            
            # Check for common issues
            if '```' in data['content']:
                blocks = re.findall(r'```(\w*)', data['content'])
                if '' in blocks:  # Empty code fence
                    issues['malformed_code'].append({
                        'file': filepath,
                        'issue': 'Code fence without language'
                    })
        
        return dict(issues)
    
    def detect_duplicates(self, files: Dict[str, dict], 
                         similarity_threshold: float = 0.8) -> List[Tuple]:
        """Detect duplicate or near-duplicate content"""
        duplicates = []
        processed = set()
        
        file_items = list(files.items())
        for i, (path1, data1) in enumerate(file_items):
            if path1 in processed:
                continue
            
            for path2, data2 in file_items[i+1:]:
                if path2 in processed:
                    continue
                
                # Quick hash check
                hash1 = hashlib.md5(data1['content'].encode()).hexdigest()
                hash2 = hashlib.md5(data2['content'].encode()).hexdigest()
                
                if hash1 == hash2:
                    duplicates.append((path1, path2, 1.0))
                    processed.add(path2)
                elif self._calculate_similarity(data1['content'], 
                                               data2['content']) > similarity_threshold:
                    duplicates.append((path1, path2, 0.85))
        
        return duplicates
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation using common lines"""
        lines1 = set(text1.split('\n'))
        lines2 = set(text2.split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)
        return intersection / union if union > 0 else 0.0
    
    def generate_health_report(self, files: Dict[str, dict]) -> dict:
        """Generate comprehensive health report"""
        report = {
            'timestamp': self.timestamp.isoformat(),
            'total_files': len(files),
            'metrics': {
                'total_size_mb': sum(f['size'] for f in files.values()) / (1024*1024),
                'avg_file_size': sum(f['size'] for f in files.values()) / len(files) if files else 0,
                'files_with_headers': sum(1 for f in files.values() if f['has_headers']),
            },
            'checks': {
                'link_validation': self.validate_links(files),
                'freshness': self.check_freshness(files),
                'structure': self.check_structure_compliance(files),
                'orphaned_pages': self.detect_orphaned_pages(),
                'duplicates': self.detect_duplicates(files),
            },
            'summary': {}
        }
        
        # Calculate summary stats
        link_issues = len(report['checks']['link_validation'].get('broken_links', []))
        stale_docs = len(report['checks']['freshness'].get('stale_content', []))
        orphaned = len(report['checks']['orphaned_pages'])
        
        report['summary'] = {
            'broken_links': link_issues,
            'stale_documents': stale_docs,
            'orphaned_pages': orphaned,
            'status': 'PASS' if link_issues == 0 and orphaned == 0 else 'WARN'
        }
        
        return report
    
    def generate_dashboard_html(self, report: dict) -> str:
        """Generate HTML health dashboard"""
        summary = report['summary']
        metrics = report['metrics']
        checks = report['checks']
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Documentation Health Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        .status-badge {{ padding: 8px 16px; border-radius: 4px; font-weight: bold; display: inline-block; margin: 10px 0; }}
        .status-pass {{ background: #4CAF50; color: white; }}
        .status-warn {{ background: #FF9800; color: white; }}
        .status-fail {{ background: #f44336; color: white; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; border-radius: 4px; border-left: 4px solid #2196F3; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ color: #666; font-size: 12px; margin-top: 5px; }}
        .issues {{ background: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border-left: 4px solid #ffc107; }}
        .issue-item {{ margin: 5px 0; font-size: 13px; color: #333; }}
        .code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        .timestamp {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Documentation Health Dashboard</h1>
        <p class="timestamp">Generated: {report['timestamp']}</p>
        
        <div style="margin: 20px 0;">
            <strong>Overall Status:</strong>
            <div class="status-badge status-{summary['status'].lower()}">
                {summary['status']} ✓ {'✓' if summary['status'] == 'PASS' else '⚠'}
            </div>
        </div>
        
        <h2>📈 Key Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{report['total_files']}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['total_size_mb']:.1f} MB</div>
                <div class="metric-label">Total Size</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['avg_file_size']:.0f}</div>
                <div class="metric-label">Avg File Size (bytes)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['files_with_headers']}</div>
                <div class="metric-label">Files with Headers</div>
            </div>
        </div>
        
        <h2>🔍 Validation Results</h2>
        <table>
            <tr>
                <th>Check</th>
                <th>Status</th>
                <th>Count</th>
            </tr>
            <tr>
                <td>Broken Links</td>
                <td>{'✅ OK' if summary['broken_links'] == 0 else '❌ FAIL'}</td>
                <td>{summary['broken_links']}</td>
            </tr>
            <tr>
                <td>Stale Documents</td>
                <td>{'✅ OK' if summary['stale_documents'] == 0 else '⚠️ WARN'}</td>
                <td>{summary['stale_documents']}</td>
            </tr>
            <tr>
                <td>Orphaned Pages</td>
                <td>{'✅ OK' if summary['orphaned_pages'] == 0 else '❌ FAIL'}</td>
                <td>{summary['orphaned_pages']}</td>
            </tr>
        </table>
        
        <h2>⚠️ Issues Summary</h2>
        <div class="issues">
            <strong>Broken Links:</strong> {summary['broken_links']}<br>
            <strong>Stale Documents (>90 days):</strong> {summary['stale_documents']}<br>
            <strong>Orphaned Pages:</strong> {summary['orphaned_pages']}<br>
            <strong>Status:</strong> {summary['status']}
        </div>
        
        <h2>💡 Next Steps</h2>
        <ul>
            <li>Review and fix any broken links</li>
            <li>Update stale documentation</li>
            <li>Ensure all pages are linked in navigation</li>
            <li>Monitor metrics daily</li>
        </ul>
    </div>
</body>
</html>"""
        return html


def main():
    """Run documentation health check"""
    monitor = DocHealthMonitor()
    
    print("🔍 Scanning documentation files...")
    files = monitor.scan_all_files()
    print(f"✅ Scanned {len(files)} files")
    
    print("\n📊 Generating health report...")
    report = monitor.generate_health_report(files)
    
    print("\n📈 Health Check Results:")
    print(f"  Total Files: {report['total_files']}")
    print(f"  Broken Links: {report['summary']['broken_links']}")
    print(f"  Stale Documents: {report['summary']['stale_documents']}")
    print(f"  Orphaned Pages: {report['summary']['orphaned_pages']}")
    print(f"  Status: {report['summary']['status']}")
    
    # Generate HTML dashboard
    html = monitor.generate_dashboard_html(report)
    dashboard_path = Path("docs/DOC_HEALTH_DASHBOARD.html")
    dashboard_path.write_text(html)
    print(f"\n✅ Dashboard generated: {dashboard_path}")
    
    # Save JSON report
    report_path = Path("docs/.doc-health-report.json")
    report_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"✅ Report saved: {report_path}")
    
    return report['summary']['status'] == 'PASS'


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
