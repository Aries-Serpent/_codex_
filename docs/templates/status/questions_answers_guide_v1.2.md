# Guide: Questions & Answers Section (v1.2)
> Generated: 2024-11-02 15:26:48 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Q&A Steward], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Standardize usage of `questions` in the status schema for traceability.

Fields
| Field | Type | Required | Notes |
|---|---|---:|---|
| id | string (Q-XXX) | Yes | Unique question ID |
| category | enum | Yes | technical/process/architecture/security/performance/compliance/other |
| priority | enum | Yes | P0–P3 |
| owner | string | Yes | Responsible party |
| asked_utc | date-time | Yes | ISO8601 UTC |
| status | enum | Yes | Open/In Review/Answered/Deferred |
| answered_utc | date-time | No | Fill when answered |
| question | string | Yes | Full text |
| answer | string | No | Fill when answered |
| confidence | 1–5 | No | Confidence in answer |

Lifecycle
- Open → In Review → Answered/Deferred.
- Use links to CAP-/FIND-/PATCH- where applicable.
