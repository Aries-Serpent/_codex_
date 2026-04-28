#!/usr/bin/env python3
"""
Generate Workflow Docs

Purpose:
    Generates workflow_docs

Usage:
    python scripts/generate_workflow_docs.py [options]

    Examples:
    $ python scripts/generate_workflow_docs.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import sys
from pathlib import Path

import yaml


def generate_workflow_readme(workflow_path: Path) -> Path:
    """
    Generate comprehensive README for a workflow file.

    Args:
        workflow_path: Path to the workflow YAML file

    Returns:
        Path to the generated README file
    """
    try:
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️  Error parsing {workflow_path}: {e}")
        return None

    if not workflow:
        print(f"⚠️  Empty workflow: {workflow_path}")
        return None

    name = workflow.get('name', workflow_path.stem)

    readme = f"""# {name}

**Workflow File**: `{workflow_path.name}`

## Purpose

{workflow.get('# purpose', '[Automated workflow - purpose to be documented]')}

## Triggers

"""

    # Add trigger information
    if 'on' in workflow:
        triggers = workflow['on']
        if isinstance(triggers, dict):
            for trigger, config in triggers.items():
                readme += f"### {trigger}\n\n"
                if isinstance(config, dict):
                    if 'schedule' in config or trigger == 'schedule':
                        cron = config if isinstance(config, list) else config.get('cron', 'Not specified')
                        readme += f"- **Schedule**: `{cron}`\n"
                    if 'branches' in config:
                        readme += f"- **Branches**: {', '.join(config['branches'])}\n"
                    if 'paths' in config:
                        readme += f"- **Paths**: {', '.join(config['paths'][:3])}{'...' if len(config['paths']) > 3 else ''}\n"
                else:
                    readme += "- Enabled\n"
                readme += "\n"
        elif isinstance(triggers, list):
            for trigger in triggers:
                readme += f"- {trigger}\n"
        else:
            readme += f"- {triggers}\n"
    else:
        readme += "[No triggers configured]\n"

    readme += """
## Permissions Required

"""

    # Add permissions
    if 'permissions' in workflow:
        permissions = workflow['permissions']
        if isinstance(permissions, dict):
            for perm, level in permissions.items():
                readme += f"- **{perm}**: `{level}`\n"
        else:
            readme += f"- {permissions}\n"
    else:
        readme += "[Default permissions]\n"

    readme += """
## Environment Variables

"""

    # Add environment variables if present
    if 'env' in workflow:
        for key, value in workflow['env'].items():
            readme += f"- **{key}**: {value}\n"
    else:
        readme += "[None specified at workflow level]\n"

    readme += """
## Jobs

"""

    # Add jobs
    if 'jobs' in workflow:
        for job_name, job_config in workflow['jobs'].items():
            readme += f"### {job_name}\n\n"

            if isinstance(job_config, dict):
                if 'runs-on' in job_config:
                    readme += f"**Runner**: `{job_config['runs-on']}`\n\n"

                if 'steps' in job_config:
                    readme += f"**Steps**: {len(job_config['steps'])}\n\n"

                    # List key steps
                    readme += "**Key Steps**:\n"
                    for i, step in enumerate(job_config['steps'][:5], 1):  # Show first 5
                        step_name = step.get('name', step.get('uses', f'Step {i}'))
                        readme += f"{i}. {step_name}\n"

                    if len(job_config['steps']) > 5:
                        readme += f"... and {len(job_config['steps']) - 5} more steps\n"

                readme += "\n"
    else:
        readme += "[No jobs configured]\n"

    readme += """
## Secrets Used

"""

    # Try to identify secrets from the workflow
    workflow_str = str(workflow)
    if 'secrets.' in workflow_str:
        # This is a heuristic - would need more sophisticated parsing
        readme += "[Secrets referenced in workflow - see workflow file for details]\n"
    else:
        readme += "[No secrets explicitly referenced]\n"

    readme += """
## Maintenance

**Last Generated**: 2026-01-16
**Status**: Active
**Maintainer**: DevOps Team

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

*This documentation was automatically generated. For detailed configuration, refer to the workflow file.*
"""

    # Write README
    readme_path = workflow_path.parent / f"{workflow_path.stem}.md"
    with open(readme_path, 'w') as f:
        f.write(readme)

    return readme_path

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_workflow_docs.py [workflow_file|--all]")
        sys.exit(1)

    workflows_dir = Path('.github/workflows')

    if sys.argv[1] == '--all':
        workflows = list(workflows_dir.glob('*.yml'))
    else:
        workflows = [Path(sys.argv[1])]

    print(f"📚 Generating documentation for {len(workflows)} workflows")
    print("="*60)

    generated = 0
    skipped = 0
    errors = 0

    for workflow in workflows:
        if not workflow.exists():
            print(f"❌ Not found: {workflow}")
            errors += 1
            continue

        readme_path = workflow.parent / f"{workflow.stem}.md"
        if readme_path.exists():
            print(f"✓  {workflow.name} (README already exists)")
            skipped += 1
            continue

        result = generate_workflow_readme(workflow)
        if result:
            generated += 1
            print(f"✅ Generated {result.name}")
        else:
            errors += 1

    print("\n" + "="*60)
    print("📊 Documentation Statistics:")
    print(f"   Generated: {generated} READMEs")
    print(f"   Skipped: {skipped} (already exist)")
    print(f"   Errors: {errors}")
    print(f"   Total Workflows: {len(workflows)}")
    print(f"   Coverage: {((generated + skipped) / len(workflows)) * 100:.1f}%")

if __name__ == '__main__':
    main()
