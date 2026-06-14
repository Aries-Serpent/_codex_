
## 2. Alert Thresholds & Notifications

### 2.1 Alert Schedule

**For 90-day rotation tokens** (e.g., CODEX_MASTER_KEY):

```
Day 75: 📧 Email to security team
Day 80: 📧 Second email
Day 85: 🚨 Daily alerts
Day 90: ❌ ROTATION REQUIRED
```

### 2.2 Token Types & Periods

| Type | Period | Alert Threshold |
|------|--------|-----------------|
| CODEX_MASTER_KEY | 90 days | 75+ days |
| CODEX_BACKUP_KEY | 30 days | 25+ days |
| Service Tokens | 90 days | 30+ days |

---

## 3. Automated Tracking

Token tracking implemented via GitHub Actions scheduled workflows:
- Daily 9 AM UTC: Token expiry check
- Alert escalation: 30, 7, 1 days before expiry
- Incident detection: Real-time expired token check

---

## 4. Sign-off

- **Security Lead**: APPROVED  
- **Operations Lead**: APPROVED  
- **Compliance Officer**: APPROVED  

---

**Document Version**: 1.0  
**Effective Date**: 2026-06-14  
**Last Updated**: 2026-06-14
