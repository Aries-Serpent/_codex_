#!/usr/bin/env python3
"""
Phase B Enhanced Validator - Query existing runs + selective new cycles
"""

import json
import subprocess
import sqlite3
from datetime import datetime, timedelta
import sys

def query_workflow_runs(workflow_name: str, limit: int = 30) -> list:
    """Query recent workflow runs from GitHub"""
    try:
        cmd = [
            "gh", "run", "list",
            "--repo", "Aries-Serpent/_codex_",
            "--workflow", workflow_name,
            "--limit", str(limit),
            "--json", "id,status,conclusion,durationMinutes,createdAt,name,runNumber",
            "--created", ">=" + (datetime.utcnow() - timedelta(days=1)).isoformat()
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
        return []
    except Exception as e:
        print(f"Error querying runs: {e}")
        return []

def analyze_runs(workflow_name: str, runs: list) -> dict:
    """Analyze workflow runs"""
    if not runs:
        return {}
    
    total = len(runs)
    completed = sum(1 for r in runs if r.get('status') == 'completed')
    successful = sum(1 for r in runs if r.get('conclusion') == 'success')
    failed = sum(1 for r in runs if r.get('conclusion') == 'failure')
    action_required = sum(1 for r in runs if r.get('conclusion') == 'action_required')
    
    success_rate = (successful / total * 100) if total > 0 else 0
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    return {
        'workflow': workflow_name,
        'total_runs': total,
        'completed_runs': completed,
        'successful_runs': successful,
        'failed_runs': failed,
        'action_required_runs': action_required,
        'success_rate': success_rate,
        'completion_rate': completion_rate,
        'recent_runs': runs[:10]
    }

def store_in_db(workflow_name: str, metrics: dict):
    """Store metrics in SQL database"""
    try:
        conn = sqlite3.connect('/tmp/phase_b_validation.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS workflow_metrics (
            id INTEGER PRIMARY KEY,
            workflow TEXT,
            total_runs INTEGER,
            successful_runs INTEGER,
            failed_runs INTEGER,
            success_rate REAL,
            timestamp TEXT
        )''')
        
        c.execute('''INSERT INTO workflow_metrics 
            (workflow, total_runs, successful_runs, failed_runs, success_rate, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                workflow_name,
                metrics['total_runs'],
                metrics['successful_runs'],
                metrics['failed_runs'],
                metrics['success_rate'],
                datetime.utcnow().isoformat()
            )
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB error: {e}")
        return False

def main():
    workflows = [
        "workflow-execution-gate.yml",
        "validate.yml"
    ]
    
    print("\n" + "="*70)
    print("PHASE B VALIDATION - RECENT RUNS ANALYSIS")
    print("="*70 + "\n")
    
    all_metrics = {}
    overall_success_rate = 0
    total_runs = 0
    total_successful = 0
    
    for workflow in workflows:
        print(f"\n📊 Analyzing: {workflow}")
        print("-" * 70)
        
        # Query recent runs
        runs = query_workflow_runs(workflow, limit=50)
        
        if runs:
            metrics = analyze_runs(workflow, runs)
            all_metrics[workflow] = metrics
            
            # Store in DB
            store_in_db(workflow, metrics)
            
            print(f"  Total runs (last 24h): {metrics['total_runs']}")
            print(f"  Completed: {metrics['completed_runs']} ({metrics['completion_rate']:.1f}%)")
            print(f"  Successful: {metrics['successful_runs']}")
            print(f"  Failed: {metrics['failed_runs']}")
            print(f"  Action Required: {metrics['action_required_runs']}")
            print(f"  Success rate: {metrics['success_rate']:.1f}%")
            
            total_runs += metrics['total_runs']
            total_successful += metrics['successful_runs']
        else:
            print(f"  ⚠️  No runs found for {workflow}")
    
    # Overall metrics
    overall_success_rate = (total_successful / total_runs * 100) if total_runs > 0 else 0
    
    print("\n" + "="*70)
    print("PHASE B OVERALL METRICS")
    print("="*70)
    print(f"Total runs: {total_runs}")
    print(f"Total successful: {total_successful}")
    print(f"Overall success rate: {overall_success_rate:.1f}%")
    print("="*70 + "\n")
    
    # Gate decision
    if overall_success_rate >= 95:
        print("🟢 PATH A: PHASE B SUCCESSFUL")
        print("   Success rate ≥95%")
        print("   ✅ Phase 8-9 LAUNCH AUTHORIZED")
        return 0
    elif overall_success_rate >= 75:
        print("🟡 PATH B: ACCEPTABLE FOR PHASE B")
        print("   Success rate 75-94%")
        print("   ⚠️  Proceeding with CAUTION")
        return 1
    else:
        print("🔴 PATH C: INADEQUATE SUCCESS")
        print("   Success rate <75%")
        print("   ❌ ESCALATION REQUIRED")
        return 2

if __name__ == "__main__":
    sys.exit(main())
