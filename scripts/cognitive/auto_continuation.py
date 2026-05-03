#!/usr/bin/env python3
"""
Automated Continuation Prompt Generator

This module provides automatic generation of structured continuation prompts
for GitHub Copilot Coding Agent sessions. It:

1. Extracts session context from cognitive brain infrastructure
2. Generates prompts in multiple formats (markdown, JSON, PR comment)
3. Saves prompts to .codex/prompts/continuation/
4. Integrates with session_manager.py for state tracking

Usage:
    # Generate prompt for current session
    python scripts/cognitive/auto_continuation.py --generate

    # Generate with specific format
    python scripts/cognitive/auto_continuation.py --format pr_comment

    # Generate from action log
    python scripts/cognitive/auto_continuation.py --from-action-log --hours 4

    # Save to file
    python scripts/cognitive/auto_continuation.py --output .codex/prompts/continuation/
"""

import argparse
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Template format types
TEMPLATE_FORMATS = ['standard', 'pr_comment', 'json']


def get_repo_root() -> Path:
    """Get the repository root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent
    return Path.cwd()


def load_action_log(
    log_path: Path,
    since: Optional[datetime] = None,
    hours: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Load and filter action log entries."""
    if not log_path.exists():
        logger.warning(f"Action log not found: {log_path}")
        return []

    if hours and not since:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if since and 'timestamp' in entry:
                    try:
                        entry_time = datetime.fromisoformat(
                            entry['timestamp'].replace('Z', '+00:00')
                        )
                        if entry_time < since:
                            continue
                    except (ValueError, TypeError):
                        # Timestamp parsing failed - include entry anyway
                        logger.debug("Suppressed exception in handler", exc_info=True)
                entries.append(entry)
            except json.JSONDecodeError:
                continue

    return entries


def load_pattern_store(store_path: Path) -> Dict[str, Any]:
    """Load the pattern learning store."""
    if not store_path.exists():
        return {"patterns": {}, "statistics": {}}

    try:
        with open(store_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"patterns": {}, "statistics": {}}


def load_objectives(objectives_path: Path) -> Dict[str, Any]:
    """Load objectives tracker and extract status."""
    if not objectives_path.exists():
        return {"primary": None, "status": "unknown"}

    content = objectives_path.read_text()

    # Extract key metrics from markdown
    objectives = {"primary": None, "aligned": True, "metrics": []}

    # Look for objective status
    if "✅ Achieved" in content:
        objectives["status"] = "achieved"
    elif "🔄 Progressing" in content or "In Progress" in content:
        objectives["status"] = "in_progress"
    else:
        objectives["status"] = "unknown"

    return objectives


def extract_session_context(
    action_entries: List[Dict[str, Any]],
    pattern_store: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract session context from action log and pattern store."""
    context = {
        "session_id": None,
        "pr_number": None,
        "started": None,
        "ended": None,
        "status": "in_progress",
        "last_phase": "unknown",
        "completed_tasks": [],
        "pending_tasks": [],
        "files_created": [],
        "files_modified": [],
        "patterns_applied": [],
        "patterns_learned": [],
        "checkpoints": [],
        "blockers": [],
        "references": [],
    }

    # Extract from action entries
    for entry in action_entries:
        action = entry.get('action', '').lower()
        path = entry.get('path', '')
        summary = entry.get('summary', '')
        timestamp = entry.get('timestamp', '')

        # Track file operations
        if action in ('create', 'created'):
            if path and path not in context["files_created"]:
                context["files_created"].append(path)
            if summary:
                context["completed_tasks"].append(f"Created {path}")

        elif action in ('edit', 'edited', 'update', 'updated'):
            if path and path not in context["files_modified"]:
                context["files_modified"].append(path)
            if summary:
                context["completed_tasks"].append(f"Updated {path}")

        # Track session info
        if not context["started"] and timestamp:
            context["started"] = timestamp
        if timestamp:
            context["ended"] = timestamp

    # Extract patterns from pattern store
    if "learning_log" in pattern_store:
        for log_entry in pattern_store["learning_log"][-3:]:
            applied = log_entry.get("patterns_applied", [])
            learned = log_entry.get("patterns_learned", [])
            context["patterns_applied"].extend(applied)
            context["patterns_learned"].extend(learned)

            if log_entry.get("session"):
                context["session_id"] = log_entry.get("session")
            if log_entry.get("pr"):
                context["pr_number"] = log_entry.get("pr")

    # Deduplicate
    context["patterns_applied"] = list(set(context["patterns_applied"]))
    context["patterns_learned"] = list(set(context["patterns_learned"]))

    return context


def generate_recommended_actions(
    context: Dict[str, Any],
    pattern_store: Dict[str, Any]
) -> List[str]:
    """Generate recommended next actions based on context."""
    actions = []

    # If there are pending tasks
    if context.get("pending_tasks"):
        actions.append(f"Continue with: {context['pending_tasks'][0]}")

    # Pattern-based recommendations
    patterns = pattern_store.get("patterns", {})
    if patterns:
        top_patterns = sorted(
            patterns.items(),
            key=lambda x: x[1].get("success_rate", 0),
            reverse=True
        )[:3]
        if top_patterns:
            actions.append(
                f"Apply high-success patterns: {', '.join(p[0] for p in top_patterns)}"
            )

    # Standard recommendations
    actions.append("Review cognitive brain objectives for alignment")
    actions.append("Validate changes with tests before committing")
    actions.append("Update action_log.ndjson with file operations")

    return actions


def generate_references(
    context: Dict[str, Any],
    repo_root: Path
) -> List[Dict[str, str]]:
    """Generate key reference links."""
    references = []

    # Standard cognitive brain references
    standard_refs = [
        ("Pattern Store", ".codex/cognitive_brain/pattern_learning_store.json"),
        ("Objectives Tracker", ".codex/cognitive_brain/objectives_tracker.md"),
        ("Session Tracker", ".codex/cognitive_brain/session_tracker.md"),
        ("Short-term Planset", ".codex/plans/cognitive_brain_short_term_planset.md"),
        ("Long-term Planset", ".codex/plans/cognitive_brain_long_term_planset.md"),
    ]

    for name, path in standard_refs:
        if (repo_root / path).exists():
            references.append({"name": name, "path": path})

    # Add recent files
    for f in context.get("files_created", [])[:3]:
        references.append({"name": f"Created: {Path(f).name}", "path": f})

    return references


def render_template(
    template_path: Path,
    context: Dict[str, Any]
) -> str:
    """Render a Jinja2-style template with context."""
    if not template_path.exists():
        logger.warning(f"Template not found: {template_path}")
        return ""

    template_content = template_path.read_text()

    # Simple template rendering (basic Jinja2-like syntax)
    # For full Jinja2, you would: from jinja2 import Template
    # But we'll do a simpler approach to avoid dependencies

    result = template_content

    # Replace simple variables {{ var }}
    for key, value in context.items():
        if isinstance(value, str):
            result = result.replace(f"{{{{ {key} }}}}", value)
        elif isinstance(value, (int, float)):
            result = result.replace(f"{{{{ {key} }}}}", str(value))
        elif isinstance(value, bool):
            result = result.replace(f"{{{{ {key} }}}}", str(value).lower())

    return result


def generate_markdown_prompt(context: Dict[str, Any]) -> str:
    """Generate a markdown continuation prompt."""
    timestamp = datetime.now(timezone.utc).isoformat()

    prompt = f"""# Session Continuation Prompt

> **Generated:** {timestamp}
> **Session ID:** {context.get('session_id', 'N/A')}
> **PR:** #{context.get('pr_number', 'N/A')}
> **Status:** {context.get('status', 'in_progress')}

---

## 🎯 Session Summary

**Started:** {context.get('started', 'N/A')}
**Last Phase:** {context.get('last_phase', 'unknown')}

### What Was Completed
"""

    for task in context.get('completed_tasks', [])[:10]:
        prompt += f"- [x] {task}\n"

    if len(context.get('completed_tasks', [])) > 10:
        prompt += f"- ... and {len(context['completed_tasks']) - 10} more\n"

    prompt += "\n### What Remains\n"
    for task in context.get('pending_tasks', []):
        prompt += f"- [ ] {task}\n"

    if not context.get('pending_tasks'):
        prompt += "- No pending tasks\n"

    prompt += f"""
---

## 📊 Session Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | {len(context.get('completed_tasks', []))} |
| Tasks Pending | {len(context.get('pending_tasks', []))} |
| Files Created | {len(context.get('files_created', []))} |
| Files Modified | {len(context.get('files_modified', []))} |
| Patterns Applied | {len(context.get('patterns_applied', []))} |

---

## 📁 Files Changed

### Created
"""

    for f in context.get('files_created', [])[:10]:
        prompt += f"- `{f}`\n"

    if len(context.get('files_created', [])) > 10:
        prompt += f"- ... and {len(context['files_created']) - 10} more\n"

    prompt += "\n### Modified\n"
    for f in context.get('files_modified', [])[:10]:
        prompt += f"- `{f}`\n"

    if len(context.get('files_modified', [])) > 10:
        prompt += f"- ... and {len(context['files_modified']) - 10} more\n"

    prompt += "\n---\n\n## 🎯 Recommended Next Actions\n\n"

    for i, action in enumerate(context.get('recommended_actions', []), 1):
        prompt += f"{i}. {action}\n"

    prompt += "\n---\n\n## 🔗 Key References\n\n"

    for ref in context.get('references', []):
        prompt += f"- {ref['name']}: `{ref['path']}`\n"

    prompt += f"""
---

## 📋 Activation Command

```
@copilot {context.get('activation_command', 'Continue with pending tasks')}
```

---

**Generated By:** Automated Continuation Prompt Generator
**Template:** standard.md
"""

    return prompt


def generate_pr_comment_prompt(context: Dict[str, Any]) -> str:
    """Generate a PR comment format prompt."""
    timestamp = datetime.now(timezone.utc).isoformat()

    tasks_total = len(context.get('completed_tasks', [])) + len(context.get('pending_tasks', []))

    prompt = f"""## 📋 Session Continuation

> **Session:** {context.get('session_id', 'N/A')} | **PR:** #{context.get('pr_number', 'N/A')} | **Status:** {context.get('status', 'in_progress')}

**Completed:** {len(context.get('completed_tasks', []))}/{tasks_total} tasks
**Files:** {len(context.get('files_created', []))} created, {len(context.get('files_modified', []))} modified
**Last Phase:** {context.get('last_phase', 'unknown')}

### ✅ Done
"""

    for task in context.get('completed_tasks', [])[-5:]:
        prompt += f"- {task}\n"

    if len(context.get('completed_tasks', [])) > 5:
        prompt += f"- ... and {len(context['completed_tasks']) - 5} more\n"

    prompt += "\n### 📝 Pending\n"

    for task in context.get('pending_tasks', [])[:5]:
        prompt += f"- {task}\n"

    if len(context.get('pending_tasks', [])) > 5:
        prompt += f"- ... and {len(context['pending_tasks']) - 5} more\n"

    if not context.get('pending_tasks'):
        prompt += "- No pending tasks\n"

    prompt += f"""
### 🔄 Continue With

```
@copilot {context.get('activation_command', 'Continue with pending tasks')}
```
"""

    if context.get('blockers'):
        prompt += "\n### ⚠️ Blockers\n"
        for blocker in context['blockers']:
            prompt += f"- {blocker}\n"

    prompt += f"\n---\n*Generated: {timestamp}*"

    return prompt


def generate_json_prompt(context: Dict[str, Any]) -> str:
    """Generate a JSON format prompt."""
    timestamp = datetime.now(timezone.utc).isoformat()

    output = {
        "version": "1.0.0",
        "generated": timestamp,
        "session": {
            "id": context.get("session_id"),
            "pr_number": context.get("pr_number"),
            "status": context.get("status", "in_progress"),
            "started": context.get("started"),
            "ended": context.get("ended"),
            "phase": context.get("last_phase", "unknown")
        },
        "tasks": {
            "completed": context.get("completed_tasks", []),
            "pending": context.get("pending_tasks", []),
            "completion_rate": (
                len(context.get("completed_tasks", [])) /
                max(1, len(context.get("completed_tasks", [])) + len(context.get("pending_tasks", [])))
            )
        },
        "files": {
            "created": context.get("files_created", []),
            "modified": context.get("files_modified", [])
        },
        "patterns": {
            "applied": context.get("patterns_applied", []),
            "learned": context.get("patterns_learned", [])
        },
        "checkpoints": context.get("checkpoints", []),
        "metrics": {
            "tasks_completed": len(context.get("completed_tasks", [])),
            "tasks_pending": len(context.get("pending_tasks", [])),
            "files_created": len(context.get("files_created", [])),
            "files_modified": len(context.get("files_modified", [])),
            "patterns_applied": len(context.get("patterns_applied", []))
        },
        "recommended_actions": context.get("recommended_actions", []),
        "references": context.get("references", []),
        "activation_command": context.get("activation_command", "Continue with pending tasks"),
        "blockers": context.get("blockers", [])
    }

    return json.dumps(output, indent=2)


def save_prompt(
    prompt: str,
    output_dir: Path,
    format_type: str,
    session_id: Optional[str] = None
) -> Path:
    """Save the generated prompt to a file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    session_part = f"_{session_id}" if session_id else ""

    if format_type == "json":
        filename = f"continuation{session_part}_{timestamp}.json"
    else:
        filename = f"continuation{session_part}_{timestamp}.md"

    output_path = output_dir / filename
    output_path.write_text(prompt)

    logger.info(f"Saved prompt to: {output_path}")
    return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Continuation Prompt Generator"
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help="Generate a continuation prompt"
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=TEMPLATE_FORMATS,
        default='standard',
        help="Output format (standard, pr_comment, json)"
    )
    parser.add_argument(
        '--from-action-log',
        action='store_true',
        help="Extract context from action log"
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help="Hours of action log to analyze (default: 24)"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Output directory for generated prompts"
    )
    parser.add_argument(
        '--session-id',
        type=str,
        help="Session ID for the prompt"
    )
    parser.add_argument(
        '--pr',
        type=int,
        help="PR number for the prompt"
    )
    parser.add_argument(
        '--pending-tasks',
        type=str,
        nargs='+',
        help="Pending tasks to include"
    )
    parser.add_argument(
        '--activation-command',
        type=str,
        default="Continue with pending tasks",
        help="Activation command for the prompt"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress informational output"
    )

    args = parser.parse_args()

    if not args.generate and not args.from_action_log:
        parser.print_help()
        return

    repo_root = get_repo_root()

    # Load data sources
    action_log_path = repo_root / '.codex' / 'action_log.ndjson'
    pattern_store_path = repo_root / '.codex' / 'cognitive_brain' / 'pattern_learning_store.json'
    # objectives_tracker.md is loaded via pattern store

    # Extract context
    if args.from_action_log:
        action_entries = load_action_log(action_log_path, hours=args.hours)
        pattern_store = load_pattern_store(pattern_store_path)
        context = extract_session_context(action_entries, pattern_store)
    else:
        context = {
            "session_id": args.session_id,
            "pr_number": args.pr,
            "status": "in_progress",
            "completed_tasks": [],
            "pending_tasks": args.pending_tasks or [],
            "files_created": [],
            "files_modified": [],
            "patterns_applied": [],
            "patterns_learned": [],
            "checkpoints": [],
            "blockers": [],
        }
        pattern_store = load_pattern_store(pattern_store_path)

    # Override with CLI args
    if args.session_id:
        context["session_id"] = args.session_id
    if args.pr:
        context["pr_number"] = args.pr
    if args.pending_tasks:
        context["pending_tasks"] = args.pending_tasks

    context["activation_command"] = args.activation_command

    # Generate recommendations and references
    context["recommended_actions"] = generate_recommended_actions(context, pattern_store)
    context["references"] = generate_references(context, repo_root)

    # Generate prompt based on format
    if args.format == 'json':
        prompt = generate_json_prompt(context)
    elif args.format == 'pr_comment':
        prompt = generate_pr_comment_prompt(context)
    else:
        prompt = generate_markdown_prompt(context)

    # Output
    if args.output:
        output_dir = Path(args.output)
        save_prompt(prompt, output_dir, args.format, context.get("session_id"))

    if not args.quiet:
        print(prompt)


if __name__ == "__main__":
    main()
