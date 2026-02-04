# Hand-off Tracking Template

---

## 📊 Hand-off Tracking Table

| **HO-ID** | **From** | **To** | **Phase** | **Status** | **Comment Link** | **Timestamp** | **Response Time** |
|-----------|----------|--------|-----------|------------|------------------|---------------|-------------------|
| HO-001 | User | Copilot | Pre-commit 3-4 | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-002 | Copilot | Codex | Pre-commit 3-4 Review | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-003 | Codex | Copilot | Pre-commit 5-8 | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-004 | Copilot | Codex | Pre-commit 5-8 Review | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-005 | Codex | Copilot | Pre-commit 9-12 | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-006 | Copilot | Codex | Pre-commit 9-12 Review | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-007 | Codex | Copilot | Pre-commit 13-16 | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-008 | Copilot | Codex | Pre-commit 13-16 Review | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-009 | Codex | Copilot | Pre-commit 17-20 (Pass 1-3) | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-010 | Copilot | Codex | Pre-commit 17-20 Review | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-011 | Codex | Copilot | Pre-commit 17-20 (Pass 4-5) | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-012 | Copilot | Codex | Pre-commit 17-20 Approval | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-013 | Codex | Copilot | Pre-commit 21-24 | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-014 | Copilot | Codex | Merge Approval | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |
| HO-015 | Codex | Copilot | Follow-up Generation | {status} | [{link_text}]({comment_url}) | {timestamp} | {response_time} |

---

## 📊 Status Codes

| Icon | Status | Description |
|------|--------|-------------|
| ⏳ | **Pending** | Awaiting trigger or initiation |
| 🔄 | **In Progress** | Agent currently working on task |
| ✅ | **Complete** | Hand-off successful, acknowledged |
| ❌ | **Failed** | Hand-off failed, requires intervention |
| 🔁 | **Retry** | Rework requested, agent re-executing |
| ⏸️ | **Paused** | Temporarily on hold |
| ⏭️ | **Skipped** | Hand-off skipped (valid reason) |

---

## 📊 Metrics Summary

### Overall Statistics

| Metric | Value |
|--------|-------|
| **Total Hand-offs** | {total_handoffs} |
| **Completed** | {completed_count} (✅) |
| **In Progress** | {in_progress_count} (🔄) |
| **Pending** | {pending_count} (⏳) |
| **Failed** | {failed_count} (❌) |
| **Success Rate** | {success_rate}% |
| **Average Response Time** | {avg_response_time} |

### Phase Breakdown

| Phase | Hand-offs | Completed | Success Rate |
|-------|-----------|-----------|--------------|
| Pre-commit 3-4 | 2 | {pc3_4_complete} | {pc3_4_rate}% |
| Pre-commit 5-8 | 2 | {pc5_8_complete} | {pc5_8_rate}% |
| Pre-commit 9-12 | 2 | {pc9_12_complete} | {pc9_12_rate}% |
| Pre-commit 13-16 | 2 | {pc13_16_complete} | {pc13_16_rate}% |
| Pre-commit 17-20 | 4 | {pc17_20_complete} | {pc17_20_rate}% |
| Pre-commit 21-24 | 2 | {pc21_24_complete} | {pc21_24_rate}% |
| Follow-up | 1 | {followup_complete} | {followup_rate}% |

---

## 📝 Usage Example

### Active Tracking

```markdown
| **HO-ID** | **From** | **To** | **Phase** | **Status** | **Comment Link** | **Timestamp** | **Response Time** |
|-----------|----------|--------|-----------|------------|------------------|---------------|-------------------|
| HO-001 | User | Copilot | Pre-commit 3-4 | ✅ Complete | [Comment #123](https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-123) | 2026-02-04T14:00:00Z | - |
| HO-002 | Copilot | Codex | Pre-commit 3-4 Review | ✅ Complete | [Comment #124](https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-124) | 2026-02-04T14:30:00Z | 30 min |
| HO-003 | Codex | Copilot | Pre-commit 5-8 | 🔄 In Progress | [Comment #125](https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-125) | 2026-02-04T15:00:00Z | - |
| HO-004 | Copilot | Codex | Pre-commit 5-8 Review | ⏳ Pending | - | - | - |
```

---

## 🔧 Tracking Script

Update tracking table using:

```bash
python scripts/handoff/track_handoffs.py \
  --handoff-id HO-002 \
  --status complete \
  --comment-url "https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-124" \
  --timestamp "2026-02-04T14:30:00Z" \
  --response-time "30min"
```

View tracking table:

```bash
python scripts/handoff/track_handoffs.py --show
```

Generate metrics:

```bash
python scripts/handoff/track_handoffs.py --metrics
```

---

## 📊 JSON Tracking File

**Location**: `.codex/handoff_tracking.json`

**Structure**:
```json
{
  "pr_number": 3145,
  "handoffs": [
    {
      "id": "HO-001",
      "from_agent": "User",
      "to_agent": "Copilot",
      "phase": "Pre-commit 3-4",
      "status": "complete",
      "comment_link": "https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-123",
      "timestamp": "2026-02-04T14:00:00Z",
      "response_time": null,
      "deliverables": [
        "coverage_baseline.md",
        "gap_analysis.json",
        "test_mapping.md"
      ]
    },
    {
      "id": "HO-002",
      "from_agent": "Copilot",
      "to_agent": "Codex",
      "phase": "Pre-commit 3-4 Review",
      "status": "complete",
      "comment_link": "https://github.com/Aries-Serpent/_codex_/pull/3145#issuecomment-124",
      "timestamp": "2026-02-04T14:30:00Z",
      "response_time": "30min",
      "deliverables": [
        "review_report.md",
        "validation_checklist.md"
      ]
    }
  ],
  "metrics": {
    "total_handoffs": 15,
    "completed": 2,
    "in_progress": 1,
    "pending": 12,
    "failed": 0,
    "success_rate": 100.0,
    "average_response_time": "30min"
  }
}
```

---

## 🎯 Success Criteria

### Hand-off Quality
- ✅ All hand-offs tracked in table
- ✅ Comment links accessible
- ✅ Timestamps accurate (ISO 8601)
- ✅ Status updated promptly
- ✅ Response times calculated

### Metrics Quality
- ✅ Success rate > 95%
- ✅ Average response time < 1 hour
- ✅ Zero failed hand-offs
- ✅ Complete audit trail
- ✅ All phases represented

---

## 🔗 Integration

### Cognitive Brain
Track hand-off patterns in:
- `.codex/cognitive_brain/handoff_patterns.md`
- Learning: What makes hand-offs successful

### Automation
Integrate with:
- `.github/workflows/agent_handoff.yml`
- Automatic tracking on comment creation

---

**Template Version**: 1.0.0
**Last Updated**: 2026-02-04T14:15:00Z
**Template Type**: Hand-off Tracking Table
