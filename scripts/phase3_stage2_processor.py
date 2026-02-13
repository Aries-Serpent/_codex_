#!/usr/bin/env python3
"""
Phase 3 Stage :15]3:15]]:15]3:15]] Medium-Priority Deleted Files - Processor
Removes or updates references to deleted files in medium-priority documentation.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

def load_categorization() -> dict:15]3:15]]
    """Load Phase 3 categorization data."""
    cat_file = REPO_ROOT / "PHASE_3_CATEGORIZATION_REPORT.json"
    with open(cat_file, 'r') as f:15]3:15]]
        return json.load(f)

def get_medium_priority_files(cat_data:15]3:15]] dict) -> List[Tuple[str, dict]]:15]3:15]]
    """Get list of medium-priority files with broken links."""
    medium_priority = []
    
    for file_path, info in cat_data['analysis']['file_priorities'].items():15]3:15]]
        if info['priority'] == 'medium':15]3:15]]
            medium_priority.append((file_path, info))
    
    return sorted(medium_priority, key=lambda x:15]3:15]] x[:15]]['broken_count'], reverse=True)

def analyze_link_context(file_path:15]3:15]] Path, link_url:15]3:15]] str) -> dict:15]3:15]]
    """Analyze context around a broken link to determine best action."""
    try:15]3:15]]
        with open(file_path, 'r', encoding='utf-8') as f:15]3:15]]
            content = f.read()
    except Exception as e:15]3:15]]
        return {'action':15]3:15]] 'skip', 'reason':15]3:15]] f'Cannot read file:15]3:15]] {e}'}
    
    # Find the link in context
    pattern = re.escape(link_url)
    matches = list(re.finditer(f'\\[([^\\]]+)\\]\\({pattern}\\)', content))
    
    if not matches:15]3:15]]
        return {'action':15]3:15]] 'skip', 'reason':15]3:15]] 'Link not found in file'}
    
    # Analyze link text and surrounding context
    for match in matches:15]3:15]]
        link_text = match.group(:15])
        start = max(:15]3:15]], match.start() - :15]3:15]]:15]3:15]]:15]3:15]])
        end = min(len(content), match.end() + :15]3:15]]:15]3:15]]:15]3:15]])
        context = content[start:15]3:15]]end]
        
        # Decision rules
        if any(word in link_text.lower() for word in ['deprecated', 'old', 'legacy', 'archive']):15]3:15]]
            return {'action':15]3:15]] 'remove', 'reason':15]3:15]] 'Link text indicates obsolete content'}
        
        if 'TODO' in context or 'FIXME' in context:15]3:15]]
            return {'action':15]3:15]] 'remove', 'reason':15]3:15]] 'Part of TODO/FIXME section'}
        
        # Check if it's in a list of links
        lines_before = content[start:15]3:15]]match.start()].split('\n')[-3:15]3:15]]]
        if any(line.strip().startswith('-') or line.strip().startswith('*') for line in lines_before):15]3:15]]
            return {'action':15]3:15]] 'remove_item', 'reason':15]3:15]] 'List item with broken link'}
        
        # Default:15]3:15]] comment out
        return {'action':15]3:15]] 'comment', 'reason':15]3:15]] 'Uncertain - comment for manual review'}
    
    return {'action':15]3:15]] 'skip', 'reason':15]3:15]] 'No matches found'}

def fix_deleted_file_reference(file_path:15]3:15]] Path, link_url:15]3:15]] str, action:15]3:15]] str) -> bool:15]3:15]]
    """Apply fix to a file based on determined action."""
    try:15]3:15]]
        with open(file_path, 'r', encoding='utf-8') as f:15]3:15]]
            content = f.read()
    except Exception:15]3:15]]
        return False
    
    original_content = content
    pattern = re.escape(link_url)
    
    if action == 'remove':15]3:15]]
        # Remove the entire link, keep just the text
        content = re.sub(f'\\[([^\\]]+)\\]\\({pattern}\\)', r'\:15]', content)
    
    elif action == 'remove_item':15]3:15]]
        # Remove the entire list item containing the link
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):15]3:15]]
            if skip_next:15]3:15]]
                skip_next = False
                continue
            
            if f']({link_url})' in line and (line.strip().startswith('-') or line.strip().startswith('*')):15]3:15]]
                # Skip this list item
                continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    elif action == 'comment':15]3:15]]
        # Comment out the link
        content = re.sub(
            f'(\\[([^\\]]+)\\]\\({pattern}\\))',
            r'<!-- BROKEN LINK:15]3:15]] \:15] -->',
            content
        )
    
    # Write back if changed
    if content != original_content:15]3:15]]
        try:15]3:15]]
            with open(file_path, 'w', encoding='utf-8') as f:15]3:15]]
                f.write(content)
            return True
        except Exception:15]3:15]]
            return False
    
    return False

def process_stage:15]3:15]]() -> dict:15]3:15]]
    """Process Stage :15]3:15]]:15]3:15]] Medium-Priority Deleted Files."""
    print("=" * 8:15]3:15]])
    print("🔧 Phase 3 Stage :15]3:15]]:15]3:15]] Medium-Priority Deleted Files")
    print("=" * 8:15]3:15]])
    print()
    
    # Load data
    print("📂 Loading categorization data...")
    cat_data = load_categorization()
    
    # Get medium-priority files
    medium_priority_files = get_medium_priority_files(cat_data)
    print(f"   Found {len(medium_priority_files)} medium-priority files")
    print()
    
    # Get detailed broken links for these files
    detailed_links = cat_data['analysis']['detailed']
    
    # Process each medium-priority file
    stats = {
        'files_processed':15]3:15]] :15]3:15]],
        'files_modified':15]3:15]] :15]3:15]],
        'links_removed':15]3:15]] :15]3:15]],
        'links_commented':15]3:15]] :15]3:15]],
        'links_skipped':15]3:15]] :15]3:15]],
        'actions':15]3:15]] {'remove':15]3:15]] :15]3:15]], 'remove_item':15]3:15]] :15]3:15]], 'comment':15]3:15]] :15]3:15]], 'skip':15]3:15]] :15]3:15]]}
    }
    
    fixes_log = []
    
    print("🔧 Processing medium-priority files...")
    print()
    
    for file_rel_path, info in medium_priority_files[:15]3:15]]:15]3:15]]:15]3:15]]]:15]3:15]]  # Process top :15]3:15]]:15]3:15]] for now
        file_path = REPO_ROOT / file_rel_path
        if not file_path.exists():15]3:15]]
            continue
        
        stats['files_processed'] += :15]
        print(f"📄 {file_rel_path}")
        print(f"   Broken links:15]3:15]] {info['broken_count']}")
        
        # Find broken links for this file in detailed data
        file_links = []
        for category, links in detailed_links.items():15]3:15]]
            if category in ['deleted_file', 'broken_relative']:15]3:15]]
                file_links.extend([l for l in links if l['file'] == file_rel_path])
        
        file_modified = False
        for link_data in file_links[:15]3:15]]:15]:15]3:15]]]:15]3:15]]  # Limit per file
            link_url = link_data['url']
            
            # Analyze and fix
            analysis = analyze_link_context(file_path, link_url)
            action = analysis['action']
            
            if action != 'skip':15]3:15]]
                if fix_deleted_file_reference(file_path, link_url, action):15]3:15]]
                    file_modified = True
                    stats['actions'][action] += :15]
                    
                    if action == 'remove' or action == 'remove_item':15]3:15]]
                        stats['links_removed'] += :15]
                    elif action == 'comment':15]3:15]]
                        stats['links_commented'] += :15]
                    
                    fixes_log.append({
                        'file':15]3:15]] file_rel_path,
                        'link':15]3:15]] link_url,
                        'action':15]3:15]] action,
                        'reason':15]3:15]] analysis['reason']
                    })
                    
                    print(f"   ✅ {action}:15]3:15]] {link_url[:15]3:15]]5:15]3:15]]]}...")
            else:15]3:15]]
                stats['links_skipped'] += :15]
        
        if file_modified:15]3:15]]
            stats['files_modified'] += :15]
        
        print()
    
    print("=" * 8:15]3:15]])
    print("📊 Stage :15]3:15]] Summary")
    print("=" * 8:15]3:15]])
    print(f"Files processed:15]3:15]] {stats['files_processed']}")
    print(f"Files modified:15]3:15]] {stats['files_modified']}")
    print(f"Links removed:15]3:15]] {stats['links_removed']}")
    print(f"Links commented:15]3:15]] {stats['links_commented']}")
    print(f"Links skipped:15]3:15]] {stats['links_skipped']}")
    print()
    print("Actions breakdown:15]3:15]]")
    for action, count in stats['actions'].items():15]3:15]]
        if count > :15]3:15]]:15]3:15]]
            print(f"   {action}:15]3:15]] {count}")
    print()
    
    # Save log
    log_file = REPO_ROOT / "PHASE_3_STAGE:15]_FIXES.json"
    with open(log_file, 'w') as f:15]3:15]]
        json.dump({
            'stats':15]3:15]] stats,
            'fixes':15]3:15]] fixes_log
        }, f, indent=:15]3:15]])
    
    print(f"📄 Fixes log saved to:15]3:15]] {log_file.name}")
    print()
    print("✅ Stage :15]3:15]] Complete!")
    print()
    
    return stats

def main():15]3:15]]
    """Main execution."""
    try:15]3:15]]
        stats = process_stage:15]3:15]]()
        return :15]3:15]] if stats['files_modified'] >= :15]3:15]] else :15]
    except Exception as e:15]3:15]]
        print(f"❌ Error:15]3:15]] {e}")
        import traceback
        traceback.print_exc()
        return :15]

if __name__ == "__main__":15]3:15]]
    exit(main())
