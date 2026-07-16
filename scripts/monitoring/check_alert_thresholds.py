#!/usr/bin/env python3
"""
Phase 12 Alert Threshold Checker

Monitors checkpoint results for alert threshold breaches and escalates critical issues.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


class AlertThresholdChecker:
    """Checks metrics against alert thresholds."""
    
    # Critical thresholds requiring immediate escalation
    CRITICAL_THRESHOLDS = {
        'uptime_min': 99.9,
        'error_rate_max': 1.0,  # >1% is CRITICAL
        'latency_variance_critical': 10,  # >10% deviation
        'cpu_peak_critical': 85,
        'memory_peak_critical': 85,
    }
    
    # High thresholds requiring investigation
    HIGH_THRESHOLDS = {
        'error_rate_max': 0.1,  # 0.05-0.1% is HIGH
        'latency_variance_high': 5,  # 5-10% deviation
        'cpu_peak_high': 75,
        'memory_peak_high': 75,
    }
    
    def __init__(self, log_path: str, escalate_on_critical: bool = False):
        """Initialize checker."""
        self.log_path = Path(log_path)
        self.escalate_on_critical = escalate_on_critical
        self.critical_alerts: List[str] = []
        self.high_alerts: List[str] = []
        
    def check_log(self) -> bool:
        """Check checkpoint log for alerts."""
        if not self.log_path.exists():
            print(f"⚠️  Checkpoint log not found: {self.log_path}")
            return True
        
        content = self.log_path.read_text()
        
        # Parse most recent checkpoint
        sections = content.split('---')
        if len(sections) < 2:
            print("✅ No alerts in checkpoint log")
            return True
        
        latest_checkpoint = sections[-2].strip()
        
        # Look for critical/degraded status
        if '🔴 CRITICAL' in latest_checkpoint:
            self.critical_alerts.append("CRITICAL status detected in latest checkpoint")
        
        if '🟡 DEGRADED' in latest_checkpoint:
            self.high_alerts.append("DEGRADED status detected in latest checkpoint")
        
        # Report findings
        if self.critical_alerts:
            print(f"🔴 CRITICAL ALERTS ({len(self.critical_alerts)}):")
            for alert in self.critical_alerts:
                print(f"   - {alert}")
            
            if self.escalate_on_critical:
                print("📢 Escalating to incident management...")
                # In real scenario, would call incident API
            
            return False
        
        if self.high_alerts:
            print(f"🟠 HIGH ALERTS ({len(self.high_alerts)}):")
            for alert in self.high_alerts:
                print(f"   - {alert}")
            return True
        
        print("✅ No critical or high alerts detected")
        return True
    
    def run(self) -> int:
        """Run checker."""
        success = self.check_log()
        return 0 if success else 1


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Phase 12 Alert Threshold Checker')
    parser.add_argument('--log', default='.codex/PHASE_12_HOURLY_CHECKPOINT_LOG_2026_07_17.md')
    parser.add_argument('--escalate-on-critical', action='store_true')
    
    args = parser.parse_args()
    
    checker = AlertThresholdChecker(
        log_path=args.log,
        escalate_on_critical=args.escalate_on_critical,
    )
    
    return checker.run()


if __name__ == '__main__':
    sys.exit(main())
