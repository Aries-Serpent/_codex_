#!/usr/bin/env python3
"""
Documentation Link Validator and Fixer
Fixes broken relative links in documentation that point outside docs/ directory
"""

import os
import re
from collections import defaultdict
from pathlib import Path

# Repository configuration - can be overridden via environment variables
REPO_OWNER = os.getenv("GITHUB_REPOSITORY_OWNER", "Aries-Serpent")
REPO_NAME = os.getenv("GITHUB_REPOSITORY_NAME", "_codex_")
# nosemgrep: url-substring-check - trusted repository base URL for documentation repair
REPO_BASE_URL = os.getenv("REPO_BASE_URL", f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main")
REPO_ROOT = Path(os.getenv("REPO_ROOT", os.getcwd()))
DOCS_ROOT = REPO_ROOT / "docs"

class LinkFixer:
    def __init__(self):
        self.fixes = []
        self.errors = []
        self.stats = defaultdict(int)

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in docs/"""
        return list(DOCS_ROOT.rglob("*.md"))

    def extract_links(self, content: str) -> list[tuple[str, str, str]]:
        """Extract all markdown links [text](url)"""
        # Match [text](url) pattern
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, content)
        return [(match[0], match[1], f"[{match[0]}]({match[1]})") for match in matches]

    def is_relative_link(self, url: str) -> bool:
        """Check if link is relative (not http/https/mailto/etc)"""
        return not url.startswith(('http://', 'https://', 'mailto:', '#', 'ftp://'))

    def resolve_path(self, current_file: Path, link_url: str) -> Path:
        """Resolve relative path from current file"""
        # Remove anchor if present
        url_without_anchor = link_url.split('#')[0]
        if not url_without_anchor:
            return None  # Pure anchor link

        # Resolve relative path
        current_dir = current_file.parent
        return (current_dir / url_without_anchor).resolve()

    def is_outside_docs(self, target_path: Path) -> bool:
        """Check if target path is outside docs/ directory"""
        try:
            target_path.relative_to(DOCS_ROOT)
            return False
        except ValueError:
            return True

    def path_to_github_url(self, target_path: Path, anchor: str = "") -> str:
        """Convert absolute path to GitHub URL"""
        try:
            rel_path = target_path.relative_to(REPO_ROOT)
            github_url = f"{REPO_BASE_URL}/{rel_path}"
            if anchor:
                github_url += f"#{anchor}"
            return github_url
        except ValueError:
            return None

    def check_file_exists(self, target_path: Path) -> bool:
        """Check if target file exists"""
        return target_path.exists()

    def fix_link(self, current_file: Path, link_text: str, link_url: str, full_link: str) -> tuple[str, str]:
        """
        Fix a single link if needed
        Returns: (new_full_link, reason) or (None, None) if no fix needed
        """
        # Skip non-relative links
        if not self.is_relative_link(link_url):
            self.stats['skipped_absolute'] += 1
            return None, None

        # Extract anchor if present
        anchor = ""
        if '#' in link_url:
            url_part, anchor = link_url.split('#', 1)
        else:
            url_part = link_url

        # Skip pure anchor links (same page)
        if not url_part or url_part == "":
            self.stats['skipped_anchor'] += 1
            return None, None

        # Resolve target path
        target_path = self.resolve_path(current_file, link_url)
        if target_path is None:
            self.stats['skipped_anchor'] += 1
            return None, None

        # Check if file exists
        if not self.check_file_exists(target_path):
            self.stats['broken_missing'] += 1
            self.errors.append(f"{current_file.relative_to(REPO_ROOT)}: Broken link to missing file: {link_url}")
            return None, f"FILE_NOT_FOUND: {target_path}"

        # Check if outside docs/
        if self.is_outside_docs(target_path):
            # Convert to GitHub URL
            github_url = self.path_to_github_url(target_path, anchor)
            if github_url:
                new_link = f"[{link_text}]({github_url})"
                self.stats['fixed_outside_docs'] += 1
                return new_link, "Outside docs/ → GitHub URL"
            self.stats['error_conversion'] += 1
            self.errors.append(f"{current_file.relative_to(REPO_ROOT)}: Cannot convert to GitHub URL: {link_url}")
            return None, "CONVERSION_ERROR"

        # Link is valid and inside docs/
        self.stats['valid_internal'] += 1
        return None, None

    def process_file(self, file_path: Path) -> dict[str, any]:
        """Process a single markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"{file_path.relative_to(REPO_ROOT)}: Cannot read file: {e}")
            return None

        links = self.extract_links(content)
        if not links:
            return None

        fixes_in_file = []
        new_content = content

        for link_text, link_url, full_link in links:
            new_link, reason = self.fix_link(file_path, link_text, link_url, full_link)
            if new_link:
                fixes_in_file.append({
                    'old': full_link,
                    'new': new_link,
                    'reason': reason
                })
                # Replace only the first occurrence to avoid unintended replacements
                # If the same link appears multiple times and needs different handling,
                # process the file multiple times or track positions
                new_content = new_content.replace(full_link, new_link, 1)

        if fixes_in_file:
            return {
                'file': file_path,
                'fixes': fixes_in_file,
                'new_content': new_content
            }

        return None

    def run(self, dry_run: bool = True) -> dict[str, any]:
        """Run the link fixer on all markdown files"""
        print(f"🔍 Scanning markdown files in {DOCS_ROOT.relative_to(REPO_ROOT)}/...")
        files = self.find_markdown_files()
        print(f"📄 Found {len(files)} markdown files")

        files_to_fix = []

        for file_path in files:
            result = self.process_file(file_path)
            if result:
                files_to_fix.append(result)
                self.fixes.extend(result['fixes'])

        # Generate report
        print(f"\n{'='*70}")
        print("📊 LINK VALIDATION REPORT")
        print(f"{'='*70}")
        print(f"✅ Valid internal links: {self.stats['valid_internal']}")
        print(f"🔧 Fixed (outside docs/): {self.stats['fixed_outside_docs']}")
        print(f"⚓ Skipped (anchors only): {self.stats['skipped_anchor']}")
        print(f"🌐 Skipped (absolute URLs): {self.stats['skipped_absolute']}")
        print(f"❌ Broken (missing files): {self.stats['broken_missing']}")
        print(f"⚠️  Conversion errors: {self.stats['error_conversion']}")
        print(f"\n📁 Files with fixes needed: {len(files_to_fix)}")
        print(f"🔗 Total links fixed: {len(self.fixes)}")

        if self.errors:
            print(f"\n⚠️  ERRORS FOUND ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20
                print(f"   - {error}")
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more")

        if files_to_fix:
            print("\n📝 FILES TO FIX:")
            for item in files_to_fix[:10]:  # Show first 10
                rel_path = item['file'].relative_to(REPO_ROOT)
                print(f"\n   {rel_path} ({len(item['fixes'])} fixes):")
                for fix in item['fixes'][:3]:  # Show first 3 fixes per file
                    print(f"      • {fix['old']}")
                    print(f"        → {fix['new']}")
                if len(item['fixes']) > 3:
                    print(f"      ... and {len(item['fixes']) - 3} more")
            if len(files_to_fix) > 10:
                print(f"\n   ... and {len(files_to_fix) - 10} more files")

        # Apply fixes if not dry run
        if not dry_run and files_to_fix:
            print(f"\n💾 Applying fixes to {len(files_to_fix)} files...")
            for item in files_to_fix:
                try:
                    item['file'].write_text(item['new_content'], encoding='utf-8')
                    print(f"   ✅ {item['file'].relative_to(REPO_ROOT)}")
                except Exception as e:
                    print(f"   ❌ {item['file'].relative_to(REPO_ROOT)}: {e}")
            print("✨ Done!")
        elif dry_run:
            print("\n🔍 DRY RUN - No files modified. Run with --apply to apply fixes.")

        return {
            'files_to_fix': files_to_fix,
            'stats': dict(self.stats),
            'errors': self.errors
        }

if __name__ == "__main__":
    import sys

    dry_run = '--apply' not in sys.argv

    fixer = LinkFixer()
    result = fixer.run(dry_run=dry_run)

    # Exit code based on results
    if result['errors']:
        sys.exit(1)
    sys.exit(0)
