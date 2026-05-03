#!/usr/bin/env python3
"""
Comprehensive broken link fixer for documentation
Handles various types of broken links including:
- Regex patterns that aren't real links
- Template placeholders
- Invalid markdown link syntax
- Missing files
- Incorrect relative paths
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
DOCS_ROOT = REPO_ROOT / "docs"

class ComprehensiveLinkFixer:
    def __init__(self):
        self.fixes = []
        self.stats = {
            'regex_patterns_removed': 0,
            'code_blocks_fixed': 0,
            'template_placeholders_removed': 0,
            'invalid_links_removed': 0,
            'missing_files_removed': 0,
            'paths_corrected': 0,
            'broken_blob_urls_removed': 0
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

        # Fix 1: Remove regex patterns that are incorrectly parsed as links
        # Example: `["\']([a-zA-Z0-9]{20,})`
        regex_pattern = r'\[(["\'])?\]\((\[[^\]]+\]|[^\)]*\{[^\}]*\}|[^\)]*[\[\]\(\)][^\)]*)\)'
        matches = re.findall(regex_pattern, content)
        if matches:
            for match in matches:
                old_link = f'[{match[0] if match[0] else ""}]({match[1]})'
                # Convert to inline code
                content = content.replace(old_link, f'`{match[1]}`')
                self.stats['regex_patterns_removed'] += 1
                self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed regex pattern link: {old_link}")

        # Fix 2: Fix code examples that look like links
        # Example: [ClassName](config={self._config})
        code_link_pattern = r'\[([A-Za-z_][A-Za-z0-9_]*)\]\(([a-z_]+=[^\)]+|[a-z_]+|None|""?|\'\'?|"[^"]*"|state\[[^\]]+\]|outputs[^)]*)\)'
        matches = re.findall(code_link_pattern, content)
        if matches:
            for match in matches:
                old_link = f'[{match[0]}]({match[1]})'
                # Convert to inline code
                new_text = f'`{match[0]}({match[1]})`'
                content = content.replace(old_link, new_text)
                self.stats['code_blocks_fixed'] += 1
                self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Fixed code block: {old_link} → {new_text}")

        # Fix 3: Remove template placeholder links
        # Example: [View](.github/copilot-prompts/active/PR-{pr_number}-followup.md)
        template_pattern = r'\[[^\]]+\]\([^\)]*\{[^\}]+\}[^\)]*\)'
        matches = re.findall(template_pattern, content)
        if matches:
            for match in matches:
                # Extract just the text part
                text_match = re.search(r'\[([^\]]+)\]', match)
                if text_match:
                    replacement = text_match.group(1)
                    content = content.replace(match, replacement)
                    self.stats['template_placeholders_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed template link: {match}")

        # Fix 4: Remove blob: URLs (invalid ChatGPT artifacts)
        blob_pattern = r'\[!\[[^\]]+\]\(blob:https://[^\)]+\)\]\([^\)]+\)'
        matches = re.findall(blob_pattern, content)
        if matches:
            for match in matches:
                content = content.replace(match, '_[Image removed - invalid blob URL]_')
                self.stats['broken_blob_urls_removed'] += 1
                self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed broken blob URL")

        # Fix 5: Remove links to non-existent files with absolute paths
        # Example: [link](/tmp/IMPLEMENTATION_SUMMARY.md)
        abs_path_pattern = r'\[([^\]]+)\]\(/[^\)]+\)'
        matches = re.findall(abs_path_pattern, content)
        if matches:
            for match in matches:
                old_link_match = re.search(r'\[' + re.escape(match) + r'\]\(/[^\)]+\)', content)
                if old_link_match:
                    old_link = old_link_match.group(0)
                    # Just keep the text
                    content = content.replace(old_link, match)
                    self.stats['invalid_links_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed absolute path link: {old_link}")

        # Fix 6: Fix HTML comment placeholders
        comment_pattern = r'\[([^\]]+)\]\(<!--[^\)]*-->\)'
        matches = re.findall(comment_pattern, content)
        if matches:
            for match in matches:
                old_link_match = re.search(r'\[' + re.escape(match) + r'\]\(<!--[^\)]*-->\)', content)
                if old_link_match:
                    old_link = old_link_match.group(0)
                    content = content.replace(old_link, match)
                    self.stats['invalid_links_removed'] += 1
                    self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed HTML comment link: {old_link}")

        # Fix 7: Convert specific broken links to GitHub URLs
        # nosemgrep: url-substring-check - static repository URL replacements in repair script
        specific_fixes = {
            '/.github/docs/Copilot_Task_Execution_Protocol.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/.github/docs/Copilot_Task_Execution_Protocol.md',
            '/.github/workflows/': 'https://github.com/Aries-Serpent/_codex_/tree/main/.github/workflows',
            '/mkdocs.yml': 'https://github.com/Aries-Serpent/_codex_/blob/main/mkdocs.yml',
            '/.github/agents/github-auth-manager/README.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/github-auth-manager/README.md',
            '/.github/agents/github-security-enforcer/README.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/github-security-enforcer/README.md',
            '/.github/agents/github-workflow-optimizer/README.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/github-workflow-optimizer/README.md',
            '/AI_AGENCY_POLICY_VERIFICATION.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/AI_AGENCY_POLICY_VERIFICATION.md',
            '/.github/agents/AGENT_DEVELOPMENT_GUIDE.md': 'https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/AGENT_DEVELOPMENT_GUIDE.md',
        }

        for old_path, new_url in specific_fixes.items():
            pattern = r'\[([^\]]+)\]\(' + re.escape(old_path) + r'\)'
            matches = re.findall(pattern, content)
            for match in matches:
                old_link = f'[{match}]({old_path})'
                new_link = f'[{match}]({new_url})'
                content = content.replace(old_link, new_link)
                self.stats['paths_corrected'] += 1
                self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Fixed path: {old_path} → {new_url}")

        # Fix 8: Remove links to truly missing files within docs/
        missing_files = [
            'docs/deferred/GOOGLE_DRIVE_FUTURE_SCOPE.md',
            'CODE_OF_CONDUCT.md',
            '../workflows/CONSOLIDATION_GUIDE.md',
            'guides/serving_reproducibility.md',
            './README_ROOT.md',
            './quickstart.md',
            './guides/serving_reproducibility.md',
            '.codex/qa_walkthrough/coverage_analysis.json',
            '.codex/qa_walkthrough/test_priority_matrix.json',
            '.+?',
            '.github/agents/COGNITIVE_BRAIN_STATUS_V9_COMPLETE.md',
            '.github/agents/COGNITIVE_BRAIN_V10_ROADMAP.md',
            '.github/agents/COGNITIVE_BRAIN_CONSOLIDATED_STATUS_V10.md',
            'docs/contributing/CONTRIBUTING.md',
            'docs/CODE_REVIEW_STANDARDS.md',
            'docs/development/best_practices.md',
            '.codex/agents/link-validator-agent.md',
            'examples/zendesk/quickstart.sh',
            'examples/zendesk/README.md',
            'docs/zendesk/WORKFLOW_DIAGRAMS.md',
            'docs/zendesk_api_reference.md',
            'docs/templates/',
            'tests/mcp/',
            '.*/.*\\.md',
            '\\..*\\.md',
            'docs/guides/AGENTS.md',
            '.github/workflows/ci.yml',
            '.codex/guardrails.md',
            'docs/agent/OPERATIONAL_GUIDELINES.md',
            'docs/admin/GENESIS_SETUP_GUIDE.md',
            '.codex/deferred_items.md',
            '. github/copilot-prompts/active/PR-{pr_number}-followup.md',
            'show-trend.md',
            'store-trend.md',
            'generate-dashboard.md',
            'validate-release.md',
            '../deployment/README.md',
            '../PR-2649-followup.md',
            '../PR-2651-followup.md',
            '../docs/configuration.md',
            '../docs/training/configuration.md',
            '../docs/deployment/configuration.md',
            '../COMPREHENSIVE_GAP_ANALYSIS.md',
            '../PR_FINAL_SUMMARY.md',
            '../archive/historical_docs_20251210/INDEX.md',
            '../training/config.py',
            '../MCP_DEVELOPER_GUIDE.md',
            '../ACCEPTANCE_CRITERIA_VERIFICATION.md',
            'Dockerfile',
            '../configs/training/reasoning/baseline.yaml',
            'docs/system/CODEBASE_DASHBOARD.md',
            'link/to/commit',
            '../../issues',
            '../_codex_/CASCADE/',
            '../../../.codex/cognitive_brain.md',
        ]

        for missing_file in missing_files:
            # Escape special regex characters
            escaped = re.escape(missing_file)
            pattern = r'\[([^\]]+)\]\(' + escaped + r'\)'
            matches = re.findall(pattern, content)
            for match in matches:
                old_link = f'[{match}]({missing_file})'
                # Keep just the text
                content = content.replace(old_link, match)
                self.stats['missing_files_removed'] += 1
                self.fixes.append(f"{file_path.relative_to(REPO_ROOT)}: Removed missing file link: {old_link}")

        # Return result
        modified = content != original_content
        return content, modified

    def process_all_files(self, apply=False):
        """Process all markdown files in docs/"""
        files = list(DOCS_ROOT.rglob("*.md"))
        print(f"📄 Processing {len(files)} markdown files...")

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
        print("📊 COMPREHENSIVE LINK FIX REPORT")
        print(f"{'='*70}")
        print(f"🔧 Regex patterns removed: {self.stats['regex_patterns_removed']}")
        print(f"💻 Code blocks fixed: {self.stats['code_blocks_fixed']}")
        print(f"📝 Template placeholders removed: {self.stats['template_placeholders_removed']}")
        print(f"❌ Invalid links removed: {self.stats['invalid_links_removed']}")
        print(f"📁 Missing file links removed: {self.stats['missing_files_removed']}")
        print(f"✅ Paths corrected: {self.stats['paths_corrected']}")
        print(f"🖼️  Broken blob URLs removed: {self.stats['broken_blob_urls_removed']}")
        print(f"\n📦 Total fixes: {sum(self.stats.values())}")
        print(f"📄 Files modified: {len(modified_files)}")

        if self.fixes:
            print("\n🔍 Sample fixes (first 20):")
            for fix in self.fixes[:20]:
                print(f"   • {fix}")
            if len(self.fixes) > 20:
                print(f"   ... and {len(self.fixes) - 20} more")

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

    fixer = ComprehensiveLinkFixer()
    has_changes = fixer.process_all_files(apply=apply)

    sys.exit(0 if not has_changes else (0 if apply else 1))
