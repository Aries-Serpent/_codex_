#!/usr/bin/env python3
"""
Phase 2D: Complex File Disambiguation
Fixes relocated file references with context-aware path resolution.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ComplexFileDisambiguator:
    """Disambiguates complex file references (README.md, INDEX.md, ARCHITECTURE.md)"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.stats = {
            'files_scanned': 0,
            'links_found': 0,
            'links_fixed': 0,
            'ambiguous_cases': 0,
            'errors': []
        }

        # Build index of target files
        self.readme_files = self._index_files('README.md')
        self.index_files = self._index_files('INDEX.md')
        self.architecture_files = self._index_files('ARCHITECTURE.md')

    def _index_files(self, filename: str) -> Dict[str, Path]:
        """Index all instances of a specific filename in the repository"""
        index = {}
        for path in self.repo_root.rglob(filename):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in ['.git', 'node_modules', '__pycache__', '.venv']):
                continue
            # Use relative path from repo root as key
            rel_path = path.relative_to(self.repo_root)
            # Create key from directory path (unique identifier)
            dir_key = str(rel_path.parent) if rel_path.parent != Path('.') else 'root'
            index[dir_key] = rel_path
        return index

    def _find_closest_file(self, source_file: Path, target_filename: str,
                          file_index: Dict[str, Path]) -> Optional[Path]:
        """Find the most contextually appropriate target file"""
        source_dir = source_file.parent

        # Strategy 1: Check same directory
        same_dir_key = str(source_dir) if source_dir != Path('.') else 'root'
        if same_dir_key in file_index:
            return file_index[same_dir_key]

        # Strategy 2: Check parent directories (climb up)
        current = source_dir
        while current != Path('.'):
            parent_key = str(current)
            if parent_key in file_index:
                return file_index[parent_key]
            if current.parent == current:
                break
            current = current.parent

        # Strategy 3: Check subdirectories (commonly referenced child)
        # For docs/ linking to specific subsystem docs
        potential_targets = []
        for dir_key, target_path in file_index.items():
            target_dir = target_path.parent
            # Check if target is logically related (same branch of tree)
            if self._is_related_path(source_dir, target_dir):
                # Calculate "distance" (directory depth difference)
                distance = self._calculate_path_distance(source_dir, target_dir)
                potential_targets.append((distance, target_path))

        if potential_targets:
            # Return closest related file
            potential_targets.sort(key=lambda x: x[0])
            return potential_targets[0][1]

        # Strategy 4: Apply domain-specific rules
        return self._apply_domain_rules(source_file, target_filename, file_index)

    def _is_related_path(self, source_dir: Path, target_dir: Path) -> bool:
        """Check if two paths are related (share common ancestry)"""
        source_parts = source_dir.parts
        target_parts = target_dir.parts

        # At least 1 common directory component (excluding root)
        if len(source_parts) > 0 and len(target_parts) > 0:
            return source_parts[0] == target_parts[0]
        return False

    def _calculate_path_distance(self, source_dir: Path, target_dir: Path) -> int:
        """Calculate logical distance between two paths"""
        source_parts = source_dir.parts
        target_parts = target_dir.parts

        # Find common prefix length
        common_prefix = 0
        for s, t in zip(source_parts, target_parts):
            if s == t:
                common_prefix += 1
            else:
                break

        # Distance = steps up from source + steps down to target
        steps_up = len(source_parts) - common_prefix
        steps_down = len(target_parts) - common_prefix
        return steps_up + steps_down

    def _apply_domain_rules(self, source_file: Path, target_filename: str,
                           file_index: Dict[str, Path]) -> Optional[Path]:
        """Apply domain-specific disambiguation rules"""
        source_dir = source_file.parent
        source_parts = source_dir.parts

        if target_filename == 'README.md':
            # Root-level references from docs/
            if 'docs' in source_parts and source_dir.parts[0] == 'docs':
                if len(source_parts) == 1:  # Top-level docs file
                    return Path('README.md') if 'root' in file_index else None

            # Agent references
            if 'agents' in source_parts and 'agents' in file_index:
                return file_index['agents']

            # GitHub agents references
            if '.github' in source_parts and 'agents' in source_parts:
                github_agents_key = '.github/agents'
                if github_agents_key in file_index:
                    return file_index[github_agents_key]

        elif target_filename == 'INDEX.md':
            # Match by primary directory
            if 'docs' in source_parts:
                # Find INDEX in same docs subdirectory
                for key, path in file_index.items():
                    if 'docs' in path.parts and len(path.parts) == len(source_parts):
                        if path.parts[:len(source_parts)-1] == source_parts[:len(source_parts)-1]:
                            return path

        elif target_filename == 'ARCHITECTURE.md':
            # Main docs architecture
            if 'docs' in source_parts and len(source_parts) <= 2:
                if 'docs' in file_index:
                    return file_index['docs']

            # Agent architecture
            if 'agents' in source_parts or '.github' in source_parts:
                if '.github/agents' in file_index:
                    return file_index['.github/agents']

        return None

    def _fix_relative_link(self, source_file: Path, old_link: str,
                          target_file: Path) -> str:
        """Generate correct relative link from source to target"""
        source_dir = source_file.parent

        # Calculate relative path
        try:
            # Get common path
            rel_path = os.path.relpath(target_file, source_dir)
            # Normalize to use forward slashes
            rel_path = rel_path.replace('\\', '/')
            # Ensure it starts with ./ if in same or subdirectory
            if not rel_path.startswith('..'):
                rel_path = './' + rel_path
            return rel_path
        except ValueError:
            # Different drives on Windows or other issue
            # Fall back to absolute GitHub URL
            return f"https://github.com/Aries-Serpent/_codex_/blob/main/{target_file}"

    def _extract_links(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract markdown links and their components"""
        # Pattern: [text](link)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = []
        for match in re.finditer(pattern, content):
            full_match = match.group(0)
            link_text = match.group(1)
            link_url = match.group(2)
            links.append((full_match, link_text, link_url))
        return links

    def _is_complex_file_link(self, link_url: str) -> Optional[str]:
        """Check if link references a complex file (README, INDEX, ARCHITECTURE)"""
        link_lower = link_url.lower()

        # Skip external links
        if link_url.startswith(('http://', 'https://')):
            # Only process GitHub repo links to these files
            if 'github.com/Aries-Serpent/_codex_' in link_url:
                if '/README.md' in link_url:
                    return 'README.md'
                if '/INDEX.md' in link_url:
                    return 'INDEX.md'
                if '/ARCHITECTURE.md' in link_url:
                    return 'ARCHITECTURE.md'
            return None

        # Skip anchors only
        if link_url.startswith('#'):
            return None

        # Check for our target files
        if 'readme.md' in link_lower:
            return 'README.md'
        if 'index.md' in link_lower:
            return 'INDEX.md'
        if 'architecture.md' in link_lower:
            return 'ARCHITECTURE.md'

        return None

    def _verify_link(self, source_file: Path, link_url: str) -> bool:
        """Verify if a link target exists"""
        # Handle GitHub URLs
        if link_url.startswith('https://github.com/Aries-Serpent/_codex_/blob/main/'):
            rel_path = link_url.replace('https://github.com/Aries-Serpent/_codex_/blob/main/', '')
            target = self.repo_root / rel_path
            return target.exists()

        # Handle relative paths
        source_dir = source_file.parent

        # Remove anchor if present
        link_path = link_url.split('#')[0]

        # Resolve relative path
        target = (source_dir / link_path).resolve()

        # Check if within repo and exists
        try:
            target.relative_to(self.repo_root)
            return target.exists()
        except ValueError:
            return False

    def process_file(self, file_path: Path) -> Dict:
        """Process a single markdown file"""
        result = {
            'file': str(file_path),
            'links_found': 0,
            'links_fixed': 0,
            'fixes': []
        }

        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            links = self._extract_links(content)

            for full_match, link_text, link_url in links:
                # Check if this is a complex file link
                target_filename = self._is_complex_file_link(link_url)
                if not target_filename:
                    continue

                result['links_found'] += 1

                # Verify if link is already valid
                if self._verify_link(file_path, link_url):
                    continue  # Link is valid, skip

                # Find appropriate target
                if target_filename == 'README.md':
                    file_index = self.readme_files
                elif target_filename == 'INDEX.md':
                    file_index = self.index_files
                else:  # ARCHITECTURE.md
                    file_index = self.architecture_files

                target_file = self._find_closest_file(file_path, target_filename, file_index)

                if target_file:
                    # Generate correct link
                    new_link_url = self._fix_relative_link(file_path, link_url, target_file)
                    new_full_match = f"[{link_text}]({new_link_url})"

                    # Replace in content
                    content = content.replace(full_match, new_full_match, 1)

                    result['links_fixed'] += 1
                    result['fixes'].append({
                        'old': full_match,
                        'new': new_full_match,
                        'target': str(target_file)
                    })
                else:
                    self.stats['ambiguous_cases'] += 1

            # Write back if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                self.stats['links_fixed'] += result['links_fixed']

            self.stats['links_found'] += result['links_found']

        except Exception as e:
            self.stats['errors'].append(f"{file_path}: {e!s}")
            result['error'] = str(e)

        return result

    def process_repository(self) -> Dict:
        """Process all markdown files in priority directories"""
        results = []

        # Priority directories
        priority_dirs = ['docs', '.github', '.codex']

        for priority_dir in priority_dirs:
            dir_path = self.repo_root / priority_dir
            if not dir_path.exists():
                continue

            for md_file in dir_path.rglob('*.md'):
                # Skip excluded directories
                if any(excluded in md_file.parts for excluded in ['.git', 'node_modules', '__pycache__']):
                    continue

                self.stats['files_scanned'] += 1
                result = self.process_file(md_file)

                if result['links_fixed'] > 0 or result['links_found'] > 0:
                    results.append(result)

        return {
            'stats': self.stats,
            'results': results
        }

def main():
    """Main execution"""
    repo_root = os.getcwd()

    print("=" * 80)
    print("Phase 2D: Complex File Disambiguation")
    print("=" * 80)
    print()

    print("Initializing disambiguator...")
    disambiguator = ComplexFileDisambiguator(repo_root)

    print("Indexed files:")
    print(f"  - README.md: {len(disambiguator.readme_files)} instances")
    print(f"  - INDEX.md: {len(disambiguator.index_files)} instances")
    print(f"  - ARCHITECTURE.md: {len(disambiguator.architecture_files)} instances")
    print()

    print("Processing markdown files...")
    output = disambiguator.process_repository()

    # Save detailed results
    output_file = repo_root + '/PHASE_2D_DISAMBIGUATION_RESULTS.json'
    with open(output_file, 'w') as f:
        json.dump(output, indent=2, fp=f)

    # Print summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    stats = output['stats']
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Complex file links found: {stats['links_found']}")
    print(f"Links fixed: {stats['links_fixed']}")
    print(f"Ambiguous cases: {stats['ambiguous_cases']}")
    print(f"Errors: {len(stats['errors'])}")
    print()

    if stats['errors']:
        print("Errors encountered:")
        for error in stats['errors'][:10]:  # Show first 10
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print()
    print(f"Detailed results saved to: {output_file}")
    print()

    # Show sample fixes
    if output['results']:
        print("Sample fixes applied:")
        fix_count = 0
        for result in output['results']:
            if result['links_fixed'] > 0:
                print(f"\n{result['file']}:")
                for fix in result['fixes'][:3]:  # Show first 3 fixes per file
                    print(f"  ✓ {fix['old']}")
                    print(f"    → {fix['new']}")
                fix_count += 1
                if fix_count >= 5:  # Show 5 files max
                    break

    print()
    print("=" * 80)
    print("Phase 2D: COMPLETE")
    print("=" * 80)

    return 0 if len(stats['errors']) == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())
