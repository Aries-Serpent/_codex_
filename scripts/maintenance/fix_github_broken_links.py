#!/usr/bin/env python3
"""
Fix broken links in .github directory files
"""

import re
import sys
from pathlib import Path

# Get repository root dynamically - can be overridden via CLI argument
if len(sys.argv) > 1 and sys.argv[1] not in ['--apply']:
    REPO_ROOT = Path(sys.argv[1]).resolve()
    sys.argv.pop(1)  # Remove from args so --apply still works
else:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # scripts/maintenance/ is 2 levels deep
GITHUB_ROOT = REPO_ROOT / ".github"

class GitHubLinkFixer:
    def __init__(self):
        self.fixes = []
        self.stats = {
            'missing_files_removed': 0,
            'paths_corrected': 0,
            'template_placeholders_removed': 0,
        }

    def fix_file(self, file_path: Path) -> tuple[str, bool]:
        """Fix all broken links in a single file"""
        # Initialize variables before try-except to avoid uninitialized variable errors
        content = ""
        modified = False

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Cannot read {file_path}: {e}")
            return content, False

        original_content = content

        # Fix 1: Remove template placeholder links
        template_pattern = r'\[([^\]]+)\]\([^\)]*\{[^\}]+\}[^\)]*\)'
        matches = re.findall(template_pattern, content)
        if matches:
            for match in matches:
                old_link_match = re.search(r'\[' + re.escape(match) + r'\]\([^\)]*\{[^\}]+\}[^\)]*\)', content)
                if old_link_match:
                    old_link = old_link_match.group(0)
                    content = content.replace(old_link, match)
                    self.stats['template_placeholders_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed template link: {old_link}")

        # Fix 2: Fix specific broken paths
        # nosemgrep: url-substring-check - repository URL substitution in maintenance script
        specific_fixes = {
            '.github/actions/README.md': '../actions/',
            '.github/workflows/CACHE_ANALYSIS_REPORT.md': None,  # Remove
            '.github/workflows/README_SCAN_SECRETS_VARIABLES.md': None,  # Remove
            '../../PHASE_10_MASTER_INTEGRATION_PLANSET.md': None,  # Remove
            '../../../.codex/cognitive_brain.md': None,  # Remove
            '../../issues': 'https://github.com/Aries-Serpent/_codex_/issues',
            '../_codex_/CASCADE/': None,  # Remove
            '.github/agents/COGNITIVE_BRAIN_STATUS_V9_COMPLETE.md': None,  # Remove
            '.github/agents/COGNITIVE_BRAIN_V10_ROADMAP.md': None,  # Remove
            '.github/agents/COGNITIVE_BRAIN_CONSOLIDATED_STATUS_V10.md': None,  # Remove
            '.github/workflows/ci.yml': '../workflows/',
            '.github/copilot-prompts/active/PR-{pr_number}-followup.md': None,  # Remove
            '../.github/workflows/': '../workflows/',
            '.github/agents/docs/CHANGELOG.md': None,  # Remove
            './.github/agents/workflow-ci-fixer.agent.md': None,  # Remove
            '.github/agents/codebase-qa-walkthrough-agent/README.md': None,  # Remove
            '.github/workflows/FLATTEN_REPO_README.md': None,  # Remove
        }

        for old_path, new_path in specific_fixes.items():
            pattern = r'\[([^\]]+)\]\(' + re.escape(old_path) + r'\)'
            matches = re.findall(pattern, content)
            for match in matches:
                old_link = f'[{match}]({old_path})'
                if new_path:
                    new_link = f'[{match}]({new_path})'
                    content = content.replace(old_link, new_link)
                    self.stats['paths_corrected'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Fixed path: {old_path} → {new_path}")
                else:
                    content = content.replace(old_link, match)
                    self.stats['missing_files_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed missing file link: {old_link}")

        # Fix 3: Remove external links to non-existent branch files
        external_broken_pattern = r'\[([^\]]+)\]\(https://github\.com/Aries-Serpent/_codex_/raw/refs/heads/0D_base_/[^\)]+\)'
        matches = re.findall(external_broken_pattern, content)
        if matches:
            for match in matches:
                old_link_match = re.search(r'\[' + re.escape(match) + r'\]\(https://github\.com/Aries-Serpent/_codex_/raw/refs/heads/0D_base_/[^\)]+\)', content)
                if old_link_match:
                    old_link = old_link_match.group(0)
                    content = content.replace(old_link, match)
                    self.stats['missing_files_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed broken external link: {old_link}")

        # Return result
        modified = content != original_content
        return content, modified

    def process_all_files(self, apply=False):
        """Process all markdown files in .github/"""
        files = list(GITHUB_ROOT.rglob("*.md"))
        print(f"📄 Processing {len(files)} markdown files in .github/...")

        modified_files = []

        for file_path in files:
            # Initialize variables to avoid uninitialized variable errors
            new_content = ""
            modified = False
            new_content, modified = self.fix_file(file_path)

            if modified:
                modified_files.append((file_path, new_content))

        # Report
        print(f"\n{'='*70}")
        print("📊 .GITHUB LINK FIX REPORT")
        print(f"{'='*70}")
        print(f"✅ Paths corrected: {self.stats['paths_corrected']}")
        print(f"📝 Template placeholders removed: {self.stats['template_placeholders_removed']}")
        print(f"❌ Missing file links removed: {self.stats['missing_files_removed']}")
        print(f"\n📦 Total fixes: {sum(self.stats.values())}")
        print(f"📄 Files modified: {len(modified_files)}")

        if self.fixes:
            print("\n🔍 All fixes:")
            for fix in self.fixes:
                print(f"   • {fix}")

        # Apply changes
        if apply and modified_files:
            print(f"\n💾 Applying changes to {len(modified_files)} files...")
            for file_path, new_content in modified_files:
                try:
                    file_path.write_text(new_content, encoding='utf-8')
                    print(f"   ✅ {file_path.relative_to(REPO_ROOT)}")
                except Exception as e:
                    print(f"   ❌ {file_path.relative_to(REPO_ROOT)}: {e}")
            print("✨ Done!")
        elif not apply:
            print("\n🔍 DRY RUN - No files modified. Run with --apply to apply fixes.")

        return len(modified_files) > 0

if __name__ == "__main__":
    import sys

    apply = '--apply' in sys.argv

    fixer = GitHubLinkFixer()
    has_changes = fixer.process_all_files(apply=apply)

    sys.exit(0 if not has_changes else (0 if apply else 1))
