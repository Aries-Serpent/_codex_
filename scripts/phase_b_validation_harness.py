from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
#!/usr/bin/env python3
"""
Phase B Validation Harness - Execute 10+ cycles per workflow
Authority: D-tier autonomous
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Optional
import sys

class ValidationHarness:
    def __init__(self):
        self.results = []
        self.start_time = datetime.utcnow()
        
    def trigger_workflow(self, workflow_name: str, cycle_num: int) -> Optional[int]:
        """Trigger a workflow and return run_id"""
        try:
            print(f"[Cycle {cycle_num}] Triggering {workflow_name}...")
            
            cmd = [
                "gh", "workflow", "run", workflow_name,
                "--repo", "Aries-Serpent/_codex_",
                "-f", f"cycle_number={cycle_num}",
                "-f", f"validation_phase=phase_b"
            ]
            
            # Special handling for different workflows
            if "workflow-execution-gate.yml" in workflow_name:
                cmd.extend(["-f", "pr_number=0"])
            elif "validate.yml" in workflow_name:
                cmd.extend(["-f", "mode=fast"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Extract run_id from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if 'created' in line.lower() or 'queued' in line.lower():
                        print(f"  ✓ Workflow triggered: {line}")
                        return None  # Will query via list-runs
                return None
            else:
                print(f"  ✗ Error triggering workflow: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            return None
    
    def wait_for_completion(self, workflow_name: str, max_wait_seconds: int = 300) -> dict:
        """Wait for most recent workflow run to complete"""
        start = time.time()
        
        while time.time() - start < max_wait_seconds:
            try:
                cmd = [
                    "gh", "run", "list",
                    "--repo", "Aries-Serpent/_codex_",
                    "--workflow", workflow_name,
                    "--limit", "1",
                    "--json", "status,conclusion,durationMinutes,createdAt,name,id,runNumber"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout:
                    data = json.loads(result.stdout)
                    if data and len(data) > 0:
                        run = data[0]
                        
                        if run['status'] == 'completed':
                            print(f"  ✓ Workflow completed: {run['conclusion']}")
                            return {
                                'run_id': run['id'],
                                'status': run['status'],
                                'conclusion': run['conclusion'],
                                'duration_minutes': run.get('durationMinutes', 0),
                                'created_at': run['createdAt'],
                                'run_number': run.get('runNumber', 0)
                            }
                        else:
                            elapsed = int(time.time() - start)
                            print(f"  ⏳ Status: {run['status']} (elapsed: {elapsed}s)")
            except Exception as e:
                print(f"  ⚠️  Query error: {e}")
            
            time.sleep(10)  # Check every 10 seconds
        
        print(f"  ✗ Timeout waiting for completion (>{max_wait_seconds}s)")
        return {
            'status': 'timeout',
            'conclusion': 'failure',
            'run_id': None
        }
    
    def execute_cycle(self, workflow_name: str, cycle_num: int) -> dict:
        """Execute one validation cycle"""
        print(f"\n{'='*60}")
        print(f"CYCLE {cycle_num}: {workflow_name}")
        print(f"{'='*60}")
        
        cycle_start = datetime.utcnow()
        
        # Trigger workflow
        self.trigger_workflow(workflow_name, cycle_num)
        time.sleep(5)  # Brief wait before checking
        
        # Wait for completion
        result = self.wait_for_completion(workflow_name, max_wait_seconds=300)
        
        cycle_end = datetime.utcnow()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        
        record = {
            'cycle_id': f"{workflow_name.split('.')[0]}-{cycle_num}",
            'workflow_name': workflow_name,
            'cycle_number': cycle_num,
            'run_id': result.get('run_id'),
            'status': result.get('status', 'unknown'),
            'conclusion': result.get('conclusion', 'unknown'),
            'duration_seconds': cycle_duration,
            'timestamp': cycle_start.isoformat(),
            'commit_sha': self.get_commit_sha()
        }
        
        self.results.append(record)
        
        # Print summary
        success = result.get('conclusion') == 'success'
        symbol = "✅" if success else "❌"
        print(f"{symbol} Conclusion: {result.get('conclusion', 'unknown')}")
        print(f"⏱️  Duration: {cycle_duration:.0f}s")
        
        return record
    
    def get_commit_sha(self) -> str:
        """Get current commit SHA"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def run_validation(self, workflows: list, cycles_per_workflow: int = 10):
        """Execute full validation suite"""
        print("\n" + "="*60)
        print("PHASE B VALIDATION HARNESS - COMPREHENSIVE CYCLES")
        print("="*60)
        print(f"Start time: {self.start_time.isoformat()}Z")
        print(f"Workflows: {', '.join(workflows)}")
        print(f"Cycles per workflow: {cycles_per_workflow}")
        print(f"Expected total: {len(workflows) * cycles_per_workflow} runs")
        print("="*60 + "\n")
        
        for workflow in workflows:
            print(f"\n🔄 Starting validation for: {workflow}")
            for cycle in range(1, cycles_per_workflow + 1):
                try:
                    self.execute_cycle(workflow, cycle)
                    if cycle < cycles_per_workflow:
                        print("⏳ Waiting 30s before next cycle...")
                        time.sleep(30)
                except KeyboardInterrupt:
                    print("\n⚠️  Validation interrupted by user")
                    break
                except Exception as e:
                    print(f"\n✗ Error in cycle {cycle}: {e}")
    
    def calculate_metrics(self) -> dict:
        """Calculate success rate and metrics"""
        if not self.results:
            return {}
        
        total_runs = len(self.results)
        successful_runs = sum(1 for r in self.results if r['conclusion'] == 'success')
        failed_runs = sum(1 for r in self.results if r['conclusion'] == 'failure')
        action_required_runs = sum(1 for r in self.results if r['conclusion'] == 'action_required')
        
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Per-workflow metrics
        workflow_metrics = {}
        for workflow in set(r['workflow_name'] for r in self.results):
            workflow_runs = [r for r in self.results if r['workflow_name'] == workflow]
            workflow_success = sum(1 for r in workflow_runs if r['conclusion'] == 'success')
            workflow_rate = (workflow_success / len(workflow_runs) * 100) if workflow_runs else 0
            workflow_metrics[workflow] = {
                'total': len(workflow_runs),
                'successful': workflow_success,
                'success_rate': workflow_rate
            }
        
        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': failed_runs,
            'action_required_runs': action_required_runs,
            'success_rate': success_rate,
            'per_workflow': workflow_metrics
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        metrics = self.calculate_metrics()
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds() / 60
        
        report = f"""# Phase B Validation Report
Generated: {end_time.isoformat()}Z
Duration: {duration:.1f} minutes
Commit SHA: {self.results[0]['commit_sha'] if self.results else 'unknown'}

## Executive Summary

**Overall Success Rate: {metrics.get('success_rate', 0):.1f}%**

- Total Runs: {metrics.get('total_runs', 0)}
- Successful: {metrics.get('successful_runs', 0)}
- Failed: {metrics.get('failed_runs', 0)}
- Action Required: {metrics.get('action_required_runs', 0)}

## Gate Decision

"""
        
        success_rate = metrics.get('success_rate', 0)
        if success_rate >= 95:
            report += "### ✅ PATH A: PHASE B SUCCESSFUL\n\n"
            report += "- Success rate: ≥95%\n"
            report += "- **STATUS:** Phase 8-9 LAUNCH AUTHORIZED ✅\n"
            report += "- v0.2.0 release UNBLOCKED\n"
        elif success_rate >= 75:
            report += "### ⚠️  PATH B: ACCEPTABLE FOR PHASE B\n\n"
            report += "- Success rate: 75-94%\n"
            report += "- **STATUS:** Proceeding with CAUTION ⚠️\n"
            report += "- Recommend 10+ more cycles if possible\n"
        else:
            report += "### ❌ PATH C: INADEQUATE SUCCESS\n\n"
            report += "- Success rate: <75%\n"
            report += "- **STATUS:** ESCALATION REQUIRED ❌\n"
            report += "- Deep investigation and remediation needed\n"
        
        report += f"\n## Per-Workflow Metrics\n\n"
        for workflow, metrics_data in metrics.get('per_workflow', {}).items():
            report += f"### {workflow}\n"
            report += f"- Total runs: {metrics_data['total']}\n"
            report += f"- Successful: {metrics_data['successful']}\n"
            report += f"- Success rate: {metrics_data['success_rate']:.1f}%\n\n"
        
        report += f"\n## Detailed Results\n\n"
        report += "| Cycle | Workflow | Status | Conclusion | Duration (s) | Timestamp |\n"
        report += "|-------|----------|--------|------------|--------------|----------|\n"
        
        for i, result in enumerate(self.results, 1):
            conclusion_symbol = "✅" if result['conclusion'] == 'success' else "❌"
            report += f"| {result['cycle_number']} | {result['workflow_name']} | {result['status']} | {conclusion_symbol} {result['conclusion']} | {result['duration_seconds']:.0f} | {result['timestamp']} |\n"
        
        return report
    
    def save_results(self, output_file: str = str(REPO_ROOT / ".codex"/"PHASE_B_EXECUTION_REPORT.md")):
        """Save results to file"""
        report = self.generate_report()
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"\n✓ Report saved: {output_file}")
        return report

if __name__ == "__main__":
    harness = ValidationHarness()
    
    # Determine cycles from command line or default to 10
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Run validation
    workflows = [
        "workflow-execution-gate.yml",
        "validate.yml"
    ]
    
    harness.run_validation(workflows, cycles_per_workflow=cycles)
    
    # Save results
    report = harness.save_results()
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    print(report)
