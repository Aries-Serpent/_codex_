#!/usr/bin/env python3
"""
Documentation Link Validator for GitHub Pages Manager Agent

Validates all links in documentation:
- Internal markdown links
- Navigation references in mkdocs.yml
- Image references
- External URLs (cognitive_app, etc.)
- Anchor links

Usage:
    python scripts/validate_docs_links.py [--fix] [--external]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class LinkValidator:
    """Validates links in markdown documentation."""
    
    def __init__(self, root_dir: Path, check_external: bool = False, auto_fix: bool = False):
        self.root_dir = root_dir
        self.docs_dir = root_dir / "docs"
        self.check_external = check_external
        self.auto_fix = auto_fix
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.fixed: List[Dict] = []
        
    def validate_all(self) -> Tuple[int, int, int]:
        """Run all validations. Returns (errors, warnings, fixed)."""
        print("🔍 GitHub Pages Manager - Link Validation\n")
        print(f"📂 Root: {self.root_dir}")
        print(f"📚 Docs: {self.docs_dir}")
        print(f"🔗 External checks: {'enabled' if self.check_external else 'disabled'}")
        print(f"🔧 Auto-fix: {'enabled' if self.auto_fix else 'disabled'}\n")
        
        # Validate mkdocs.yml navigation
        self._validate_mkdocs_nav()
        
        # Validate all markdown files
        self._validate_markdown_files()
        
        # Validate cognitive_app accessibility
        self._validate_cognitive_app()
        
        # Report results
        self._report_results()
        
        return len(self.errors), len(self.warnings), len(self.fixed)
    
    def _validate_mkdocs_nav(self):
        """Validate mkdocs.yml navigation references."""
        print("📋 Validating mkdocs.yml navigation...")
        
        mkdocs_file = self.root_dir / "mkdocs.yml"
        if not mkdocs_file.exists():
            self.errors.append({
                "type": "missing_file",
                "file": "mkdocs.yml",
                "message": "mkdocs.yml not found"
            })
            return
        
        try:
            with open(mkdocs_file) as f:
                config = yaml.safe_load(f)
            
            nav = config.get("nav", [])
            self._check_nav_entries(nav, mkdocs_file)
            
        except Exception as e:
            self.errors.append({
                "type": "yaml_error",
                "file": str(mkdocs_file),
                "message": f"Failed to parse mkdocs.yml: {e}"
            })
    
    def _check_nav_entries(self, nav, mkdocs_file, path=""):
        """Recursively check navigation entries."""
        for item in nav:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # File reference
                        if not value.startswith("http"):
                            file_path = self.docs_dir / value
                            if not file_path.exists():
                                self.errors.append({
                                    "type": "broken_nav_link",
                                    "file": str(mkdocs_file),
                                    "link": value,
                                    "nav_title": key,
                                    "message": f"Navigation entry '{key}' references missing file: {value}"
                                })
                    elif isinstance(value, list):
                        # Nested navigation
                        self._check_nav_entries(value, mkdocs_file, f"{path}/{key}")
    
    def _validate_markdown_files(self):
        """Validate all markdown files in docs directory."""
        print(f"📄 Validating markdown files in {self.docs_dir}...")
        
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"   Found {len(md_files)} markdown files\n")
        
        for md_file in md_files:
            self._validate_markdown_file(md_file)
    
    def _validate_markdown_file(self, md_file: Path):
        """Validate links in a single markdown file."""
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append({
                "type": "read_error",
                "file": str(md_file.relative_to(self.root_dir)),
                "message": f"Failed to read file: {e}"
            })
            return
        
        # Find all markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.finditer(link_pattern, content)
        
        for match in links:
            text = match.group(1)
            url = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            self._validate_link(md_file, url, text, line_num)
    
    def _validate_link(self, md_file: Path, url: str, text: str, line_num: int):
        """Validate a single link."""
        # Skip anchor-only links
        if url.startswith('#'):
            return
        
        # Check external URLs
        if url.startswith('http://') or url.startswith('https://'):
            if self.check_external:
                self._validate_external_link(md_file, url, text, line_num)
            return
        
        # Remove anchor if present
        url_path = url.split('#')[0] if '#' in url else url
        
        # Skip empty paths
        if not url_path:
            return
        
        # Resolve relative path
        if url_path.startswith('/'):
            # Absolute path from docs root
            target = self.docs_dir / url_path.lstrip('/')
        else:
            # Relative path from current file
            target = (md_file.parent / url_path).resolve()
        
        # Check if target exists
        if not target.exists():
            # Try to find similar files for auto-fix suggestions
            similar = self._find_similar_files(target)
            
            error = {
                "type": "broken_link",
                "file": str(md_file.relative_to(self.root_dir)),
                "line": line_num,
                "link": url,
                "text": text,
                "message": f"Link to non-existent file: {url}"
            }
            
            if similar:
                error["suggestions"] = similar
            
            self.errors.append(error)
    
    def _validate_external_link(self, md_file: Path, url: str, text: str, line_num: int):
        """Validate an external URL (placeholder for future implementation)."""
        # For now, just check if it's the cognitive_app URL
        if 'cognitive_app' in url:
            self.warnings.append({
                "type": "external_link",
                "file": str(md_file.relative_to(self.root_dir)),
                "line": line_num,
                "link": url,
                "text": text,
                "message": f"External cognitive_app link (requires deployment validation): {url}"
            })
    
    def _validate_cognitive_app(self):
        """Validate cognitive_app documentation and accessibility."""
        print("🧠 Validating cognitive_app accessibility...")
        
        # Check cognitive_app.md exists
        cognitive_doc = self.docs_dir / "cognitive_app.md"
        if not cognitive_doc.exists():
            self.errors.append({
                "type": "missing_cognitive_app",
                "file": "docs/cognitive_app.md",
                "message": "cognitive_app.md documentation not found"
            })
            return
        
        # Check if cognitive_app directory exists
        cognitive_app_dir = self.root_dir / "cognitive_app"
        if not cognitive_app_dir.exists():
            self.errors.append({
                "type": "missing_cognitive_app_dir",
                "file": "cognitive_app/",
                "message": "cognitive_app source directory not found"
            })
            return
        
        # Check for key files
        key_files = [
            "package.json",
            "index.html",
            "src/main.tsx",
            "vite.config.ts"
        ]
        
        missing_files = []
        for key_file in key_files:
            if not (cognitive_app_dir / key_file).exists():
                missing_files.append(key_file)
        
        if missing_files:
            self.warnings.append({
                "type": "cognitive_app_incomplete",
                "files": missing_files,
                "message": f"cognitive_app missing key files: {', '.join(missing_files)}"
            })
        else:
            print("   ✅ cognitive_app source files present")
        
        # Verify documentation mentions live URL
        content = cognitive_doc.read_text()
        if "aries-serpent.github.io/_codex_/cognitive_app" not in content:
            self.warnings.append({
                "type": "cognitive_app_url",
                "file": "docs/cognitive_app.md",
                "message": "cognitive_app documentation doesn't mention live URL"
            })
        else:
            print("   ✅ cognitive_app live URL documented")
    
    def _find_similar_files(self, target: Path) -> List[str]:
        """Find files with similar names for suggestions."""
        target_name = target.name.lower()
        target_stem = target.stem.lower()
        
        similar = []
        
        # Search in docs directory
        for file in self.docs_dir.rglob("*"):
            if file.is_file():
                file_name = file.name.lower()
                file_stem = file.stem.lower()
                
                # Check for similar names
                if (file_stem in target_stem or target_stem in file_stem or
                    file_name == target_name):
                    rel_path = file.relative_to(self.docs_dir)
                    similar.append(str(rel_path))
        
        return similar[:3]  # Return top 3 matches
    
    def _report_results(self):
        """Print validation results."""
        print("\n" + "="*70)
        print("📊 VALIDATION RESULTS")
        print("="*70)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. {error['type'].upper()}")
                print(f"   File: {error.get('file', 'N/A')}")
                if 'line' in error:
                    print(f"   Line: {error['line']}")
                print(f"   ⚠️  {error['message']}")
                if 'link' in error:
                    print(f"   Link: {error['link']}")
                if 'suggestions' in error:
                    print(f"   Suggestions: {', '.join(error['suggestions'])}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"\n{i}. {warning['type'].upper()}")
                print(f"   {warning['message']}")
                if 'file' in warning:
                    print(f"   File: {warning['file']}")
                if 'link' in warning:
                    print(f"   Link: {warning['link']}")
        
        if self.fixed:
            print(f"\n✅ FIXED ({len(self.fixed)}):")
            for fix in self.fixed:
                print(f"   {fix['message']}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        
        print("\n" + "="*70)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings, {len(self.fixed)} fixed")
        print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate documentation links for GitHub Pages"
    )
    parser.add_argument(
        "--external",
        action="store_true",
        help="Check external URLs (slower)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix broken links where possible"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )
    
    args = parser.parse_args()
    
    validator = LinkValidator(
        root_dir=args.root,
        check_external=args.external,
        auto_fix=args.fix
    )
    
    errors, warnings, fixed = validator.validate_all()
    
    # Exit with error code if there are errors
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
