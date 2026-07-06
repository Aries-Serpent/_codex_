#!/usr/bin/env python3
"""
Track 12.3 Gate 5 Real-Time Monitoring
Monitors Release workflow success rate post-fix deployment
"""

import subprocess
import json
import sys
from datetime import datetime
from typing import List, Dict, Tuple

# Fix deployment timestamp
FIX_DEPLOYED_AT = datetime.fromisoformat("2026-07-06T05:40:00+00:00")
MONITORING_START = datetime.fromisoformat("2026-07-06T05:43:52+00:00")
SUCCESS_THRESHOLD = 0.95  # 95% success rate required
MIN_RUNS = 30

def run_gh_command(cmd: List[str]) -> str:
    """Execute GitHub CLI command"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}", file=sys.stderr)
        return ""

def get_release_runs() -> List[Dict]:
    """Fetch Release workflow runs from GitHub API"""
    cmd = [
        "gh", "api",
        "repos/Aries-Serpent/_codex_/actions/workflows/184226080/runs",
        "--paginate",
        "--jq", ".workflow_runs[] | {id: .id, number: .run_number, created_at: .created_at, conclusion: .conclusion}"
    ]
    
    output = run_gh_command(cmd)
    if not output:
        return []
    
    # Parse newline-delimited JSON
    runs = []
    for line in output.strip().split('\n'):
        if line:
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: skipping malformed JSON line: {line[:80]}", file=sys.stderr)
    return runs

def classify_runs(runs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Classify runs into pre-fix and post-fix"""
    pre_fix = []
    post_fix = []
    
    for run in runs:
        created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
        if created_at >= FIX_DEPLOYED_AT:
            post_fix.append(run)
        else:
            pre_fix.append(run)
    
    return pre_fix, post_fix

def calculate_metrics(runs: List[Dict]) -> Dict:
    """Calculate success metrics"""
    if not runs:
        return {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'success_rate': 0.0,
            'success_percent': 0.0
        }
    
    successful = sum(1 for r in runs if r.get('conclusion') == 'success')
    failed = sum(1 for r in runs if r.get('conclusion') == 'failure')
    
    success_rate = successful / len(runs) if runs else 0.0
    
    return {
        'total': len(runs),
        'successful': successful,
        'failed': failed,
        'success_rate': success_rate,
        'success_percent': success_rate * 100
    }

def determine_trend(current_rate: float, prev_rate: float = None) -> str:
    """Determine success rate trend"""
    if prev_rate is None:
        return "INITIALIZING"
    if current_rate > prev_rate:
        return "Improving ↑"
    elif current_rate < prev_rate:
        return "Declining ↓"
    else:
        return "Stable →"

def determine_gate_status(metrics: Dict, run_count: int) -> Tuple[str, str]:
    """Determine Gate 5 status based on metrics"""
    if run_count < MIN_RUNS:
        return "PENDING", f"Collecting data ({run_count}/{MIN_RUNS} runs)"
    
    if metrics['success_rate'] >= SUCCESS_THRESHOLD:
        return "PASS", f"✓ SUCCESS RATE ≥95% ({metrics['success_percent']:.1f}%)"
    elif metrics['success_rate'] >= 0.90:
        return "CAUTION", f"Borderline ({metrics['success_percent']:.1f}%, threshold 95%)"
    else:
        return "FAIL", f"✗ Below threshold ({metrics['success_percent']:.1f}%)"

def format_status_comment(check_num: int, metrics: Dict, gate_status: str, gate_msg: str, trend: str) -> str:
    """Format status comment for PR"""
    return f"""🔄 **Track 12.3 Re-Validation Status** (Check #{check_num})

**Success Rate:** {metrics['successful']}/{metrics['total']} runs ({metrics['success_percent']:.1f}%)  
**Trend:** {trend}  
**Gate 5 Status:** {gate_status}  
{gate_msg}

**Next Check:** +15 minutes  
**Monitoring Started:** 2026-07-06T05:43:52Z  
**Current Time:** {datetime.utcnow().isoformat()}Z
"""

def main():
    print("📊 Starting Track 12.3 Gate 5 Real-Time Monitoring")
    print(f"   Fix Deployed: 2026-07-06T05:40:00Z")
    print(f"   Current Time: {datetime.utcnow().isoformat()}Z")
    print(f"   Success Threshold: ≥95% ({MIN_RUNS} runs minimum)")
    
    # Fetch all runs
    all_runs = get_release_runs()
    pre_fix, post_fix = classify_runs(all_runs)
    
    print(f"\n📈 Run Classification:")
    print(f"   Pre-fix runs: {len(pre_fix)}")
    print(f"   Post-fix runs: {len(post_fix)}")
    
    if len(post_fix) == 0:
        print("\n⏳ No post-fix runs detected yet. Release workflow may not have been triggered.")
        print("    Waiting for Release workflow executions...")
        return
    
    # Calculate metrics for post-fix runs
    metrics = calculate_metrics(post_fix)
    trend = determine_trend(metrics['success_rate'])
    gate_status, gate_msg = determine_gate_status(metrics, len(post_fix))
    
    print(f"\n✅ Post-Fix Metrics:")
    print(f"   Successful: {metrics['successful']}/{metrics['total']}")
    print(f"   Success Rate: {metrics['success_percent']:.1f}%")
    print(f"   Trend: {trend}")
    print(f"   Gate 5: {gate_status}")
    
    print(f"\n📝 Status Comment:")
    status = format_status_comment(1, metrics, gate_status, gate_msg, trend)
    print(status)
    
    if gate_status == "PASS":
        print("\n🎉 GATE 5 PASS CRITERIA MET!")
        sys.exit(0)
    else:
        print(f"\n⏳ Still collecting data. Need {MIN_RUNS - len(post_fix)} more runs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
