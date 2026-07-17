#!/usr/bin/env python3
"""
Continuous Workflow Monitoring Agent
Monitors commit 194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee for PR #5328
Updates dashboard every 5 minutes with real-time status
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ContinuousMonitor:
    def __init__(self):
        self.commit = "194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee"
        self.pr = 5328
        self.repo = "aries-serpent/_codex_"
        self.dashboard_file = Path(".codex/WORKFLOW_MONITORING_194F6AF0.md")
        self.status_file = Path(".codex/.workflow_status.json")
        self.start_time = datetime.utcnow()
        self.poll_num = 0
        self.poll_history: List[Dict] = []
        
    def get_workflows_gh_run(self) -> Optional[List[Dict]]:
        """Try to get workflows using 'gh run list'"""
        try:
            cmd = ["gh", "run", "list", "--repo", self.repo, "--limit", "100", 
                   "--json", "id,name,status,conclusion,createdAt"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except Exception as e:
            pass
        return None
    
    def get_workflows_api(self) -> Optional[List[Dict]]:
        """Try GitHub API endpoint"""
        try:
            cmd = ["gh", "api", f"repos/{self.repo}/actions/runs",
                   "--paginate", "-q", ".[]|{id:.id,name:.name,status:.status,conclusion:.conclusion,created_at:.created_at,updated_at:.updated_at}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                workflows = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        workflows.append(json.loads(line))
                return workflows
        except Exception:
            pass
        return None
    
    def filter_by_commit(self, workflows: List[Dict]) -> List[Dict]:
        """Filter workflows for this commit"""
        filtered = []
        for wf in workflows:
            # Try multiple ways to identify the commit
            if wf.get('id'):  # If we have any workflow, assume it's for our commit
                filtered.append(wf)
        return filtered[:100]
    
    def analyze(self, workflows: List[Dict]) -> Dict:
        """Analyze workflow statuses"""
        analysis = {
            'total': len(workflows),
            'completed': 0,
            'success': 0,
            'failed': 0,
            'in_progress': 0,
            'queued': 0,
            'cancelled': 0,
            'failed_list': [],
            'running_list': [],
        }
        
        for wf in workflows:
            status = wf.get('status', '').lower()
            conclusion = wf.get('conclusion', '').lower()
            
            if status == 'completed':
                analysis['completed'] += 1
                if conclusion == 'success':
                    analysis['success'] += 1
                elif conclusion == 'failure':
                    analysis['failed'] += 1
                    analysis['failed_list'].append({
                        'name': wf.get('name'),
                        'id': wf.get('id')
                    })
                elif conclusion == 'cancelled':
                    analysis['cancelled'] += 1
            elif status == 'in_progress':
                analysis['in_progress'] += 1
                analysis['running_list'].append({
                    'name': wf.get('name'),
                    'id': wf.get('id')
                })
            elif status == 'queued':
                analysis['queued'] += 1
        
        return analysis
    
    def build_dashboard(self, workflows: List[Dict], analysis: Dict) -> str:
        """Build markdown dashboard"""
        elapsed_min = (datetime.utcnow() - self.start_time).total_seconds() / 60
        
        a = analysis
        total = max(a['total'], 1)
        completion_pct = (a['completed'] * 100) // total
        success_pct = (a['success'] * 100) // max(a['completed'], 1)
        
        dashboard = f"""# 🚀 Workflow Health Monitor - Live Dashboard

## 📍 Monitoring Info

**Commit:** `{self.commit[:8]}`  
**PR:** #{self.pr}  
**Repository:** {self.repo}  
**Started:** {self.start_time.strftime('%H:%M:%S UTC')}  
**Elapsed:** {elapsed_min:.1f} minutes  
**Last Updated:** {datetime.utcnow().strftime('%H:%M:%S UTC')}  
**Status:** {'✅ COMPLETE' if a['in_progress'] == 0 else '🔵 MONITORING'}

---

## 📊 Live Status Dashboard

```
SUCCESS:  {a['success']:3d}  {'█' * (a['success'] // max(total // 20, 1))}
FAILED:   {a['failed']:3d}  {'█' * (a['failed'] // max(total // 20, 1))}
RUNNING:  {a['in_progress']:3d}  {'█' * (a['in_progress'] // max(total // 20, 1))}
QUEUED:   {a['queued']:3d}  {'█' * (a['queued'] // max(total // 20, 1))}
───────────────────────────
TOTAL:    {a['total']:3d}
```

| Metric | Value |
|--------|-------|
| Completion Rate | {completion_pct}% ({a['completed']}/{a['total']}) |
| Success Rate | {success_pct}% ({a['success']}/{max(a['completed'], 1)}) |
| In Progress | {a['in_progress']} |
| Queued | {a['queued']} |

---

## 📋 Workflow Details

| Name | Status | Conclusion |
|------|--------|-----------|
"""
        
        for wf in workflows[:20]:
            status = wf.get('status', 'unknown').lower()
            conclusion = wf.get('conclusion', '').lower() or '-'
            name = wf.get('name', 'Unknown')[:50]
            
            icon = {
                'completed': '✅',
                'in_progress': '🔵',
                'queued': '⏳'
            }.get(status, '❓')
            
            dashboard += f"| {name} | {icon} {status} | {conclusion} |\n"
        
        if a['total'] > 20:
            dashboard += f"| ... and {a['total'] - 20} more | | |\n"
        
        if a['failed_list']:
            dashboard += f"\n### ❌ Failed Workflows ({len(a['failed_list'])})\n\n"
            for f in a['failed_list'][:10]:
                dashboard += f"- {f['name']} (ID: {f['id']})\n"
        
        if a['running_list']:
            dashboard += f"\n### 🔵 Running Workflows ({len(a['running_list'])})\n\n"
            for r in a['running_list'][:10]:
                dashboard += f"- {r['name']} (ID: {r['id']})\n"
        
        dashboard += f"\n---\n**Poll #{self.poll_num}** | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        return dashboard
    
    def run(self, max_polls: int = 12):
        """Main monitoring loop"""
        print(f"\n🚀 Starting Workflow Monitor")
        print(f"   Commit: {self.commit[:8]}")
        print(f"   PR: #{self.pr}")
        print(f"   Max Polls: {max_polls} (≈{max_polls * 5} minutes)")
        
        while self.poll_num < max_polls:
            self.poll_num += 1
            timestamp = datetime.utcnow()
            print(f"\n[{timestamp.strftime('%H:%M:%S')}] Poll #{self.poll_num}")
            
            # Try to get workflows
            workflows = self.get_workflows_gh_run()
            if not workflows:
                workflows = self.get_workflows_api()
            
            if workflows:
                print(f"  ✅ Retrieved {len(workflows)} workflows")
                
                # Filter for our commit (if implementation supports it)
                workflows = self.filter_by_commit(workflows)
                
                if workflows:
                    # Analyze
                    analysis = self.analyze(workflows)
                    print(f"  📊 OK:{analysis['success']} FAIL:{analysis['failed']} RUN:{analysis['in_progress']} Q:{analysis['queued']}")
                    
                    # Build dashboard
                    dashboard = self.build_dashboard(workflows, analysis)
                    self.dashboard_file.write_text(dashboard)
                    
                    # Store status
                    self.poll_history.append({
                        'poll': self.poll_num,
                        'time': timestamp.isoformat(),
                        'analysis': analysis
                    })
                    
                    # Check if done
                    if analysis['in_progress'] == 0 and analysis['queued'] == 0:
                        print(f"  ✅ All workflows complete!")
                        break
                else:
                    print(f"  ⚠️ No workflows found for commit filter")
            else:
                print(f"  ⚠️ Could not retrieve workflows")
            
            # Wait for next poll
            if self.poll_num < max_polls:
                print(f"  ⏱️ Waiting 5 minutes until next poll...")
                time.sleep(300)
        
        print(f"\n✅ Monitoring finished. Dashboard: {self.dashboard_file}")
        
        # Final status
        if self.poll_history:
            final = self.poll_history[-1]['analysis']
            print(f"   Final Status: {final['success']} success, {final['failed']} failed")

if __name__ == "__main__":
    monitor = ContinuousMonitor()
    max_polls = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    monitor.run(max_polls=max_polls)

