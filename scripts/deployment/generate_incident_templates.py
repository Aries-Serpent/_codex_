#!/usr/bin/env python3
"""
Incident Communication Templates Generator

Generates templates for incident reporting, status updates, and post-incident reviews
during deployment rollback scenarios.

Usage:
    python generate_incident_templates.py --output .codex/incident-templates
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IncidentTemplateGenerator:
    """Generates incident communication templates."""

    def __init__(self, output_dir: str = '.codex/incident-templates'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_incident_report_template(self) -> str:
        """Generate incident report template."""
        template = '''# Incident Report

**Incident ID:** [INCIDENT-YYYYMMDD-HHmm]  
**Severity:** [Critical | High | Medium | Low]  
**Status:** [Active | Mitigated | Resolved | Post-Mortem]  
**Generated:** YYYY-MM-DD HH:mm UTC  

---

## 1. Summary

**Incident Title:** [Clear, concise description of the incident]

**Duration:**
- **Start Time:** YYYY-MM-DD HH:mm UTC
- **Detection Time:** YYYY-MM-DD HH:mm UTC (detected +X minutes)
- **Mitigation Time:** YYYY-MM-DD HH:mm UTC (mitigated +X minutes)
- **Resolution Time:** YYYY-MM-DD HH:mm UTC (resolved +X minutes)
- **Total Duration:** [HH:mm]

**Impact:**
- **Affected Services:** [Service 1, Service 2, ...]
- **Users Impacted:** [Number or percentage]
- **Business Impact:** [Monetary loss, data loss, etc.]
- **System Impact:** [Uptime %, error rate increase, etc.]

---

## 2. Timeline

| Time (UTC) | Event | Action | Owner |
|-----------|-------|--------|-------|
| HH:mm | Initial detection | Alert triggered | [Team] |
| HH:mm | Investigation started | P1 oncall paged | [Owner] |
| HH:mm | Root cause identified | [Brief description] | [Owner] |
| HH:mm | Mitigation started | [Action taken] | [Owner] |
| HH:mm | Mitigation completed | [Result] | [Owner] |
| HH:mm | Monitoring confirmed resolved | All green | [Monitoring] |

---

## 3. Root Cause Analysis

### What Happened?
[Detailed narrative of what occurred, timeline of events leading to the incident]

### Why Did It Happen?
[Root cause - what underlying issue led to this incident?]

### Detection & Response
- **Detection Method:** [How was the incident detected?]
- **Detection Lag:** [Time between incident start and detection]
- **Alert Effectiveness:** [Did alerts trigger appropriately?]

---

## 4. Mitigation Actions

### Immediate Response
- [ ] [Action 1: Brief description]
- [ ] [Action 2: Brief description]
- [ ] [Action 3: Brief description]

### Deployed Workarounds
- [Workaround 1 and result]
- [Workaround 2 and result]

### Rollback Decision
- **Decision Made At:** HH:mm UTC
- **Decision Authority:** [Name, role]
- **Reason:** [Why rollback was chosen over other options]
- **Rollback Executed:** [Time and result]

---

## 5. Business Impact

### Revenue Impact
- **Estimated Loss:** $[amount]
- **Duration:** HH:mm
- **Affected Transactions:** [Number]

### Customer Impact
- **Affected Customers:** [Number]
- **Severity to Customers:** [Critical | High | Medium | Low]
- **Support Tickets Generated:** [Number]

### Reputation Impact
- **Social Media Mentions:** [If applicable]
- **Internal Communications Needed:** [Yes | No]
- **External Communications Needed:** [Yes | No]

---

## 6. Technical Details

### System Components Affected
- **Service 1:** [Brief impact description]
- **Service 2:** [Brief impact description]
- **Database:** [Any data inconsistencies?]
- **Cache Layer:** [Any cache invalidation needed?]

### Error Logs & Metrics
```
[Relevant error messages, stack traces, or metric anomalies]
```

### Configuration & State
- **Active Config Version:** [Version]
- **Deployment Revision:** [Revision number]
- **Data State:** [Consistent | Inconsistent]

---

## 7. Escalation & Communication

### Internal Escalation Path
1. **L1 Oncall (First Alert):** [Name] - notified at HH:mm
2. **L2 Engineering:** [Name] - escalated at HH:mm  
3. **L3 Leadership:** [Name] - escalated at HH:mm
4. **Executive Notification:** [Yes | No] - CEO notified at HH:mm

### External Communication
- **Customer Notification:** [Yes | No] - sent at HH:mm
- **Status Page Update:** [Yes | No] - updated at HH:mm
- **Social Media:** [Yes | No] - posted at HH:mm

### Communication Channels Used
- [ ] Slack #incidents channel
- [ ] Email to stakeholders
- [ ] Customer notification system
- [ ] Status page
- [ ] Social media

---

## 8. Prevention & Follow-up

### Immediate Actions Taken
- [ ] [Action 1 + owner + deadline]
- [ ] [Action 2 + owner + deadline]
- [ ] [Action 3 + owner + deadline]

### Short-term Improvements (1-2 weeks)
- [ ] [Improvement 1 + owner + deadline]
- [ ] [Improvement 2 + owner + deadline]

### Long-term Improvements (1-3 months)
- [ ] [Architectural change 1 + owner + deadline]
- [ ] [Architectural change 2 + owner + deadline]

### Monitoring Enhancements
- [ ] [New alert + threshold]
- [ ] [New metric + dashboard]
- [ ] [Additional health check]

---

## 9. Sign-Off

**Incident Commander:** [Name], [Title]  
**Date:** YYYY-MM-DD  
**Status:** [CONFIRMED | REQUIRES REVIEW]

**Next Review Meeting:** YYYY-MM-DD HH:mm UTC

---

## Appendix: Contact Information

See: `ESCALATION_CONTACTS.md`

'''
        return template

    def generate_status_update_template(self) -> str:
        """Generate status update template."""
        template = '''# Incident Status Update

**Incident ID:** [INCIDENT-YYYYMMDD-HHmm]  
**Update #:** [1/2/3/...]  
**Time:** YYYY-MM-DD HH:mm UTC  
**Status:** [Investigating | Mitigating | Resolved]

---

## Current Status

**Situation:** 
[Concise description of current state - 2-3 sentences]

**Impact:**
- Services Down: [Service names]
- Error Rate: [Current % increase]
- User Impact: [Brief description]

**ETA to Resolution:**
[Time estimate based on current mitigation efforts]

---

## What We're Doing

1. **Investigation:** [Current investigation status]
   - Finding: [Key technical detail]
   - Action: [What happens next]

2. **Mitigation:** [Current mitigation status]
   - Action: [What we're doing]
   - Progress: [% complete]

3. **Communication:** [Who's been notified]
   - Customers: [Yes/No]
   - Leadership: [Yes/No]

---

## What You Should Do

**For Customers Using [Service]:**
- [Recommended action 1]
- [Recommended action 2]
- [Workaround if available]

**How to Report Issues:**
- Use: `incident@company.com`
- Subject: Include `[INCIDENT-YYYYMMDD-HHmm]`

---

## Next Update

Expected in: [15 minutes | 30 minutes | 1 hour]

---

**Incident Commander:** [Name]  
**Next Update:** YYYY-MM-DD HH:mm UTC

'''
        return template

    def generate_stakeholder_notification(self) -> str:
        """Generate stakeholder notification template."""
        template = '''Subject: [ACTION NEEDED] Service Incident - [INCIDENT-YYYYMMDD-HHmm]

To: [Executive stakeholders, customer success leads, finance]

---

INCIDENT ALERT
==============

Incident ID: INCIDENT-YYYYMMDD-HHmm
Severity: [CRITICAL | HIGH | MEDIUM]
Time: YYYY-MM-DD HH:mm UTC

SITUATION
---------
[2-sentence summary of what happened]

IMPACT
------
- Affected Customers: [Number or list]
- Duration: [Time since start]
- Estimated Business Impact: $[amount] / [% revenue]

WHAT WE'RE DOING
----------------
[3-4 bullets with actions underway]

NEXT STEPS
----------
1. [Immediate action]
2. [Expected time to resolution]
3. [Communication cadence - how often you'll hear from us]

WHO TO CONTACT
--------------
Primary: [Name] - [role] - [contact]
Escalation: [Name] - [role] - [contact]

RESPONSE REQUIRED
-----------------
[ ] Acknowledge receipt (reply to this email)
[ ] Activate crisis communications team (if external communication needed)
[ ] Prepare customer communication draft (if public announcement needed)

---

Updates will be sent every [30 minutes | 1 hour] or immediately if status changes.

Real-time status: https://status.company.com
Incident channel: #incident-[id] on Slack

---

[Signed]
Incident Response Team
'''
        return template

    def generate_post_incident_review(self) -> str:
        """Generate post-incident review template."""
        template = '''# Post-Incident Review (PIR)

**Incident ID:** INCIDENT-YYYYMMDD-HHmm  
**Review Date:** YYYY-MM-DD  
**Participants:** [Names, roles]  
**Facilitator:** [Name]

---

## 1. Incident Summary

**Duration:** HH:mm (from start to full resolution)  
**Severity:** [Critical | High | Medium | Low]  
**Services Affected:** [List]  
**Root Cause:** [One sentence summary]

---

## 2. Timeline (What Happened)

| Time | Event |
|------|-------|
| HH:mm | [Event 1] |
| HH:mm | [Event 2] |
| HH:mm | [Event 3] |
| HH:mm | [Event 4] |
| HH:mm | [Event 5] |

---

## 3. Root Cause Analysis

### What Happened?
[Detailed narrative]

### Why Did It Happen? (5 Whys)

1. **Why 1:** [Immediate cause]
   - Root: [Why did immediate cause happen?]

2. **Why 2:** [Why did root 1 happen?]
   - Root: [Why did this happen?]

3. **Why 3:** [Why did root 2 happen?]
   - Root: [Why did this happen?]

4. **Why 4:** [Why did root 3 happen?]
   - Root: [Why did this happen?]

5. **Why 5:** [Fundamental root cause]

### Contributing Factors
- [Factor 1: How did this contribute?]
- [Factor 2: How did this contribute?]
- [Factor 3: How did this contribute?]

---

## 4. Response Effectiveness

### What Went Well ✅
- [Positive 1: Brief description of what worked]
- [Positive 2: Brief description of what worked]
- [Positive 3: Brief description of what worked]

### What Could Be Better 📈
- [Opportunity 1: Description of gap]
- [Opportunity 2: Description of gap]
- [Opportunity 3: Description of gap]

### How Fast Were We?
- **Detection Lag:** [Minutes to detect]
- **Response Time:** [Minutes from detection to first action]
- **Mitigation Time:** [Minutes from response to mitigation]
- **Total Resolution Time:** [HH:mm]

---

## 5. Preventive Actions

### Short-Term (1-2 weeks)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| [Implement X to prevent Y] | [Name] | YYYY-MM-DD | Pending |
| [Add alert for Z] | [Name] | YYYY-MM-DD | Pending |

### Medium-Term (1-3 months)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| [Architectural change 1] | [Name] | YYYY-MM-DD | Pending |
| [System redesign 2] | [Name] | YYYY-MM-DD | Pending |

### Long-Term (3+ months)
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| [Major refactor 1] | [Name] | YYYY-MM-DD | Pending |
| [Infrastructure change] | [Name] | YYYY-MM-DD | Pending |

---

## 6. Monitoring & Detection Improvements

### Current Gaps
- [Gap 1: We should have detected X by Y]
- [Gap 2: We should have alerted on Z]

### New Alerts to Implement
- [ ] Alert: [Condition] → threshold [value] → notify [channel]
- [ ] Alert: [Condition] → threshold [value] → notify [channel]

### Dashboards to Create
- [ ] Dashboard: [Name] - metrics [list]
- [ ] Dashboard: [Name] - metrics [list]

---

## 7. Training & Knowledge Sharing

### Team Training Needs
- [ ] [Team member] needs training on [topic]
- [ ] [Team member] needs training on [topic]

### Documentation Updates Needed
- [ ] Update runbook: [Runbook name]
- [ ] Create new documentation: [Doc name]
- [ ] Update escalation procedures

### Knowledge Sharing Plan
- Team meeting: [Date, time, attendees]
- Brown bag session: [Topic]
- Wiki/documentation updates: [Expected completion]

---

## 8. Business Metrics

### Revenue Impact
- **Estimated Loss:** $[amount]
- **Affected Transactions:** [Number]

### Reputation Impact
- **Customer Complaints:** [Number]
- **Support Tickets:** [Number]
- **Social Media Negative Mentions:** [Number]

### Operational Metrics
- **Detection Speed:** [Minutes]
- **Resolution Speed:** [Minutes]
- **Team Overtime Hours:** [Hours]

---

## 9. Lessons Learned

### What We Learned About Our Systems
1. [Learning 1: System behavior or capability]
2. [Learning 2: System behavior or capability]
3. [Learning 3: System behavior or capability]

### What We Learned About Our Processes
1. [Process 1: What worked, what didn't]
2. [Process 2: What worked, what didn't]
3. [Process 3: What worked, what didn't]

### What We Learned About Our Team
1. [Team strength 1]
2. [Team improvement area 1]
3. [Team capability to develop]

---

## 10. Action Items

**Follow-up Actions** (assign to people, set deadlines)

- [ ] [Action 1] - Assigned to [Name] - Due [Date]
- [ ] [Action 2] - Assigned to [Name] - Due [Date]
- [ ] [Action 3] - Assigned to [Name] - Due [Date]
- [ ] [Action 4] - Assigned to [Name] - Due [Date]

---

## 11. Sign-Off

**Facilitator:** [Name]  
**Date:** YYYY-MM-DD  
**Next Review:** YYYY-MM-DD (to verify action item completion)

**Approval:**
- [ ] Engineering Lead: _________________ Date: _______
- [ ] Product Manager: _________________ Date: _______
- [ ] Operations Lead: _________________ Date: _______

'''
        return template

    def generate_all_templates(self) -> bool:
        """Generate all incident templates."""
        try:
            logger.info("Generating incident communication templates...")

            templates = {
                'INCIDENT_REPORT_TEMPLATE.md': self.generate_incident_report_template(),
                'STATUS_UPDATE_TEMPLATE.md': self.generate_status_update_template(),
                'STAKEHOLDER_NOTIFICATION.txt': self.generate_stakeholder_notification(),
                'POST_INCIDENT_REVIEW.md': self.generate_post_incident_review()
            }

            for filename, content in templates.items():
                filepath = self.output_dir / filename
                filepath.write_text(content)
                logger.info(f"✅ Generated {filename}")

            # Generate README for templates directory
            readme = '''# Incident Communication Templates

This directory contains templates for incident communication during deployment rollbacks and other critical incidents.

## Templates

### 1. INCIDENT_REPORT_TEMPLATE.md
Comprehensive incident report template for documenting what happened, why it happened, and what we're doing about it.

**Use when:**
- An incident has been declared
- Need to track incident lifecycle
- Post-incident documentation

**Section overview:**
- Summary and timeline
- Root cause analysis
- Business impact
- Escalation and communication
- Prevention actions

### 2. STATUS_UPDATE_TEMPLATE.md
Brief status update for stakeholders during active incident.

**Use when:**
- Providing regular updates to stakeholders
- Communicating progress on mitigation
- Setting expectations for resolution time

**Typical frequency:** Every 30-60 minutes during active incident

### 3. STAKEHOLDER_NOTIFICATION.txt
Email notification to executive stakeholders, customer success, and finance.

**Use when:**
- Incident requires executive awareness
- Customer impact needs immediate communication
- Business/revenue implications

**Recipients:**
- CTO/VP Engineering
- VP Product
- CFO (for revenue impact)
- Customer Success Lead
- CEO (if severity = Critical)

### 4. POST_INCIDENT_REVIEW.md
Post-incident review template for blameless retrospective.

**Use when:**
- Incident is fully resolved
- Sufficient time has passed (24-72 hours)
- Team available for 1-2 hour meeting

**Goals:**
- Understand what happened
- Identify root causes
- Prevent recurrence
- Improve team capabilities

## Usage Guidelines

### Getting Started
1. Copy the template to your incident directory
2. Replace placeholder [brackets] with actual details
3. Focus on facts, not blame
4. Keep updates frequent and concise

### Best Practices
- **Clarity First:** Stakeholders want to know impact and ETA
- **Transparency:** Share what you know and don't know
- **Accuracy:** Use observed metrics, not guesses
- **Action Oriented:** Always have a next step
- **Blameless:** Focus on systems, not individuals

### Quick Reference
- **Detection Time:** Minutes from incident start to detection
- **Response Time:** Minutes from detection to first action
- **Mitigation Time:** Minutes from response to mitigation
- **Resolution Time:** Total time from start to full recovery

## Integration with Runbooks

- Link incident reports to rollback procedures
- Reference incident templates in escalation procedures
- Use post-incident reviews to improve runbooks
- Update emergency procedures based on findings

## Examples

See `.codex/rollback-procedures.md` for integration examples and full incident scenarios.

## Questions?

Contact: incident-response@company.com

'''
            readme_path = self.output_dir / 'README.md'
            readme_path.write_text(readme)
            logger.info("✅ Generated README.md")

            logger.info(f"✅ All templates generated in {self.output_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Error generating templates: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate incident communication templates'
    )
    parser.add_argument(
        '--output',
        default='.codex/incident-templates',
        help='Output directory for templates'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = IncidentTemplateGenerator(args.output)
    success = generator.generate_all_templates()

    import sys
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
