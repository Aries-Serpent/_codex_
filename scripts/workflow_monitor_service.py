#!/usr/bin/env python3
"""
Production Workflow Monitoring Service
Monitors commit 194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee continuously
Updates .codex/WORKFLOW_MONITORING_194F6AF0.md every 5 minutes
"""

import subprocess
import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ProductionWorkflowMonitor:
    def __init__(self):
        self.commit_sha = "194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee"
        self.commit_short = "194f6af0"
        self.pr_number = 5328
        self.repo = "aries-serpent/_codex_"
        self.monitoring_file = Path(".codex/WORKFLOW_MONITORING_194F6AF0.md")
        self.cache_file = Path(".codex/.workflow_cache.json")
        self.start_time = datetime.utcnow()
        self.poll_count = 0
        self.workflow_history: List[Dict[str, Any]] = []
        self.last_statuses: Dict[int, str] = {}
        
    def query_gh_api(self, endpoint: str, query: str = "") -> Tuple[bool, List[Dict]]:
        """Query GitHub API via gh CLI with timeout"""
        try:
            cmd = ["gh", "api", f"repos/{self.repo}/actions/runs", "--paginate"]
            if query:
                cmd.extend(["-q", query])
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                workflows = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            workflows.append(json.loads(line))
                        except:
                            pass
                return True, workflows
            else:
                print(f"API Error (code {result.returncode}): {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("API query timed out after 30s")
        except Exception as e:
            print(f"Exception: {e}")
        
        return False, []
    
    def fetch_workflows(self) -> List[Dict[str, Any]]:
        """Fetch and filter workflows for this commit"""
        success, all_workflows = self.query_gh_api(
            "actions/runs",
            ".[]|select(.head_sha | startswith(\"{}\"))|{{id:.id,name:.name,status:.status,conclusion:.conclusion,created_at:.created_at,updated_at:.updated_at,run_number:.run_number}}".format(self.commit_short)
        )
        
        if success:
            return all_workflows
        
        # Fall back to cache if available
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    cached = json.load(f)
                    if cached.get('workflows'):
                        print(f"  Using cached data: {len(cached['workflows'])} workflows")
                        return cached['workflows']
            except:
                pass
        
        return []
    
    def cache_workflows(self, workflows: List[Dict[str, Any]]):
        """Cache workflows for fallback"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.utcnow().isoformat(),
                    'workflows': workflows
                }, f)
        except:
            pass
    
    def analyze_workflows(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow status and metrics"""
        status_counts = {
            'total': len(workflows),
            'success': 0,
            'failed': 0,
            'running': 0,
            'queued': 0,
            'cancelled': 0,
        }
        
        running_durations = []
        failed_workflows = []
        stalled = []
        now = datetime.utcnow()
        
        for wf in workflows:
            status = wf.get('status', '').lower()
            conclusion = wf.get('conclusion', '').lower()
            
            if status == 'completed':
                if conclusion == 'success':
                    status_counts['success'] += 1
                elif conclusion == 'failure':
                    status_counts['failed'] += 1
                    failed_workflows.append({
                        'name': wf.get('name'),
                        'run_id': wf.get('id'),
                        'run_number': wf.get('run_number')
                    })
                elif conclusion == 'cancelled':
                    status_counts['cancelled'] += 1
            elif status == 'in_progress':
                status_counts['running'] += 1
                created = datetime.fromisoformat(wf.get('created_at', '').replace('Z', '+00:00'))
                duration = (now - created).total_seconds() / 60
                running_durations.append(duration)
                
                # Flag stalled (>25 min running)
                if duration > 25:
                    stalled.append({
                        'name': wf.get('name'),
                        'duration_min': round(duration, 1),
                        'id': wf.get('id')
                    })
            elif status == 'queued':
                status_counts['queued'] += 1
        
        return {
            'counts': status_counts,
            'failed': failed_workflows,
            'stalled': stalled,
            'running_durations': running_durations,
            'completion_rate': (status_counts['success'] + status_counts['failed']) / max(status_counts['total'], 1),
            'success_rate': status_counts['success'] / max(status_counts['success'] + status_counts['failed'], 1),
        }
    
    def build_dashboard(self, workflows: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Build markdown dashboard"""
        elapsed = datetime.utcnow() - self.start_time
        elapsed_min = elapsed.total_seconds() / 60
        
        c = analysis['counts']
        status_icon = "🟢" if c['running'] == 0 else "🔵"
        
        dashboard = f"""# 🚀 Workflow Health Monitor - Production

**📌 Commit:** `{self.commit_short}`  
**📋 PR:** #5328  
**🏢 Repository:** {self.repo}  
**📊 Status:** {status_icon} {'COMPLETE' if c['running'] == 0 else 'MONITORING'}  
**⏱️ Elapsed:** {elapsed_min:.1f} minutes  
**🕐 Last Update:** {datetime.utcnow().strftime('%H:%M:%S UTC')}  
**📍 Start Time:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 📊 Real-Time Status Dashboard

```
Status Overview:
  ✅ Success:   {c['success']:3d}  {'█' * (c['success'] // max(1, c['total'] // 20))}
  ❌ Failed:    {c['failed']:3d}  {'█' * (c['failed'] // max(1, c['total'] // 20))}
  🔵 Running:   {c['running']:3d}  {'█' * (c['running'] // max(1, c['total'] // 20))}
  ⏳ Queued:    {c['queued']:3d}  {'█' * (c['queued'] // max(1, c['total'] // 20))}
  ⛔ Cancelled: {c['cancelled']:3d}  {'█' * (c['cancelled'] // max(1, c['total'] // 20))}
  ───────────────────────
  📊 Total:    {c['total']:3d}
```

| Metric | Value | Status |
|--------|-------|--------|
| **Total Workflows** | {c['total']} | - |
| **Success Rate** | {analysis['success_rate']*100:.1f}% | {'🟢' if analysis['success_rate'] > 0.9 else '🟡' if analysis['success_rate'] > 0.7 else '🔴'} |
| **Completion Rate** | {analysis['completion_rate']*100:.1f}% | - |
| **In Progress** | {c['running']} | {'🟢' if c['running'] == 0 else '🟡'} |
| **Stalled Workflows** | {len(analysis['stalled'])} | {'🟢' if len(analysis['stalled']) == 0 else '🔴'} |
| **Failed Workflows** | {c['failed']} | {'🟢' if c['failed'] == 0 else '🔴'} |

---

## ⚙️ Workflow Details

| Workflow | Status | Conclusion | Run # |
|----------|--------|-----------|-------|
"""
        
        for wf in sorted(workflows, key=lambda x: x.get('id', 0), reverse=True)[:30]:
            status = wf.get('status', '').lower()
            conclusion = wf.get('conclusion', '').lower()
            name = wf.get('name', 'Unknown')[:40]
            run_num = wf.get('run_number', '?')
            
            icon = {'completed': '✅', 'in_progress': '⏳', 'queued': '⏸️'}.get(status, '❓')
            
            dashboard += f"| {name} | {icon} {status} | {conclusion or '-'} | #{run_num} |\n"
        
        if len(workflows) > 30:
            dashboard += f"| ... + {len(workflows) - 30} more | | | |\n"
        
        if analysis['stalled']:
            dashboard += f"\n### ⚠️ Stalled Workflows (Running >25 min)\n\n"
            for s in analysis['stalled']:
                dashboard += f"- **{s['name']}** → {s['duration_min']}min (ID: {s['id']})\n"
        
        if analysis['failed']:
            dashboard += f"\n### ❌ Failed Workflows\n\n"
            for f in analysis['failed'][:10]:
                dashboard += f"- **{f['name']}** (Run #{f['run_number']})\n"
        
        dashboard += f"\n---\n"
        dashboard += f"**Poll #{self.poll_count}** | **Updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        return dashboard
    
    def monitor(self, max_polls: int = 12):  # 12 polls * 5 min = 60 minutes
        """Run monitoring loop"""
        print(f"\n🚀 Workflow Monitoring Started")
        print(f"   Commit: {self.commit_short}")
        print(f"   PR: #{self.pr_number}")
        print(f"   Max Duration: {max_polls * 5} minutes ({max_polls} polls)\n")
        
        while self.poll_count < max_polls:
            self.poll_count += 1
            elapsed = datetime.utcnow() - self.start_time
            
            print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Poll #{self.poll_count} ({elapsed.total_seconds()/60:.1f}m elapsed)")
            
            # Fetch workflows
            workflows = self.fetch_workflows()
            
            if workflows:
                print(f"  ✅ Found {len(workflows)} workflows")
                self.cache_workflows(workflows)
                
                # Analyze
                analysis = self.analyze_workflows(workflows)
                
                # Print summary
                c = analysis['counts']
                print(f"  📊 OK:{c['success']} FAIL:{c['failed']} RUN:{c['running']} QUEUE:{c['queued']}")
                
                if analysis['stalled']:
                    print(f"  ⚠️  Stalled: {len(analysis['stalled'])} workflows")
                
                # Build and save dashboard
                dashboard = self.build_dashboard(workflows, analysis)
                self.monitoring_file.write_text(dashboard)
                
                # Check if done
                if c['running'] == 0 and c['queued'] == 0:
                    print(f"  ✅ All workflows completed!")
                    break
            else:
                print(f"  ⚠️  Could not fetch workflows (API unavailable?)")
            
            # Wait for next poll (except on last iteration)
            if self.poll_count < max_polls:
                print(f"  ⏱️ Next poll in 5 minutes...")
                time.sleep(300)  # 5 minutes
        
        print(f"\n✅ Monitoring complete. Dashboard: {self.monitoring_file}")

if __name__ == "__main__":
    monitor = ProductionWorkflowMonitor()
    max_polls = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    monitor.monitor(max_polls=max_polls)

