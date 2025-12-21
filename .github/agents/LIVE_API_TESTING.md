# Live API Testing Guide

Comprehensive guide for testing the deployed GitHub Agent PR Reviewer with live GitHub API.

---

## 📋 Overview

**Testing Phases:**
1. Pre-deployment smoke tests
2. Webhook endpoint validation
3. GitHub App integration test
4. End-to-end PR review test
5. Performance and load testing

**Prerequisites:**
- Deployed infrastructure (Lambda + API Gateway)
- GitHub App configured and installed
- Test repository with PR permissions

---

## 🚀 Phase 1: Pre-Deployment Smoke Tests

### Test Lambda Function Locally

```bash
# Test the main handler
cd .github/agents

python3 << 'PYTEST'
import sys
sys.path.insert(0, '.')

from codex_reviewer.main import CodexQuantumReviewer, ReviewContext
import asyncio

async def test_local():
    reviewer = CodexQuantumReviewer()
    
    context = ReviewContext(
        pr_number=1,
        repo="test/repo",
        files_changed=["test.py"],
        diff="+ print('test')",
        base_branch="main",
        head_branch="feature",
        author="testuser",
        description="Test PR"
    )
    
    event = {"action": "initial_review", "context": context}
    result = await reviewer.handle_event(event)
    
    print(f"✅ Local test result: {result}")
    assert result["status"] == "review_complete"
    print("✅ All local tests passed!")

asyncio.run(test_local())
PYTEST
```

### Test Pattern Detection

```bash
# Run pattern validation
python .github/agents/scripts/validate_patterns.py

# Expected output:
# ✅ api_key: 6/6 passed
# ✅ github_token: 4/4 passed
# Total: 19/19 passing (100%)
```

---

## 🌐 Phase 2: Webhook Endpoint Validation

### Get Webhook URL

```bash
cd .github/agents/deploy/terraform
terraform output -raw webhook_url
# Output: https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/webhook
```

### Test Endpoint Availability

```bash
WEBHOOK_URL=$(cd .github/agents/deploy/terraform && terraform output -raw webhook_url)

# Test OPTIONS (CORS preflight)
curl -X OPTIONS "${WEBHOOK_URL}" -v

# Test POST with empty payload
curl -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -d '{}' \
    -v

# Expected: 200 OK or 403 (signature verification)
```

### Test Webhook Signature Verification

```bash
# Test with invalid signature
curl -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -H "X-Hub-Signature-256: sha256=invalid" \
    -d '{"test": true}' \
    -v

# Expected: 401 Unauthorized (signature mismatch)
```

### Test with Valid Signature

```bash
# Generate valid signature
WEBHOOK_SECRET="${TF_VAR_github_webhook_secret}"
PAYLOAD='{"test": true}'
SIGNATURE=$(echo -n "${PAYLOAD}" | openssl dgst -sha256 -hmac "${WEBHOOK_SECRET}" | sed 's/^.* //')

curl -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Event: ping" \
    -H "X-Hub-Signature-256: sha256=${SIGNATURE}" \
    -d "${PAYLOAD}"

# Expected: 200 OK with response
```

---

## 🐙 Phase 3: GitHub App Integration Test

### Install GitHub App

1. Navigate to your GitHub App settings:
   ```
   https://github.com/settings/apps/YOUR_APP_NAME
   ```

2. Click "Install App"

3. Select repository: `Aries-Serpent/_codex_` (or test repo)

4. Grant requested permissions

5. Confirm installation

### Verify Installation

```bash
# Using GitHub CLI
gh api /app/installations

# Or using curl
curl -H "Authorization: Bearer $(gh auth token)" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/app/installations

# Expected: JSON with your installation
```

### Test Webhook Delivery

1. Go to GitHub App settings → Advanced → Recent Deliveries

2. Click "Redeliver" on a previous delivery (or wait for new event)

3. Check delivery status:
   - ✅ Green checkmark = success
   - ❌ Red X = failed

4. View Response:
   ```json
   {
     "status": "review_complete",
     "pr_number": 123,
     "confidence": 0.85
   }
   ```

---

## 🧪 Phase 4: End-to-End PR Review Test

### Create Test Pull Request

```bash
# Create test branch
git checkout -b test/agent-review-$(date +%s)

# Add test file with intentional issues
cat > test_file.py << 'PYEOF'
# Test file for agent review
API_KEY = "sk_test_1234567890abcdefghij"  # Secret (should be detected)

def vulnerable_query(user_input):
    query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL injection
    return query

# TODO: Add proper error handling
def risky_function():
    eval(user_input)  # Command injection
PYEOF

git add test_file.py
git commit -m "test: Add file with security issues for agent review"
git push origin HEAD
```

### Create Pull Request

```bash
# Using GitHub CLI
gh pr create \
    --title "Test: Agent Review Test PR" \
    --body "This PR tests the agent's review capabilities with intentional security issues." \
    --base main \
    --head test/agent-review-$(date +%s)

# Or manually via GitHub UI
```

### Monitor Agent Response

**Check CloudWatch Logs:**
```bash
# Stream Lambda logs
aws logs tail /aws/lambda/codex-reviewer-agent-dev --follow

# Look for:
# - "Processing PR #XXX"
# - "Detected secrets: X"
# - "Security issues: X"
# - "Posted review"
```

**Check PR for Agent Review:**

1. Navigate to PR in GitHub
2. Check "Reviewers" section - should see `codex-quantum-reviewer[bot]`
3. Check "Files changed" - should see review comments
4. Check "Conversation" - should see review summary

### Expected Agent Behavior

**Review Summary Comment:**
```markdown
## 🤖 Codex Quantum Review

**Confidence**: 75.0%
**Status**: changes_requested

### 📊 Review Summary
Found **3** suggestions across:
- security: 3 items

### 🎯 Orchestration Plan
1. Address security vulnerabilities
   ```bash
   # Remove hardcoded secrets
   # Sanitize SQL queries
   # Remove dangerous eval() calls
   ```

### 🔄 Next Steps
- [ ] Remove hardcoded API key
- [ ] Fix SQL injection vulnerability
- [ ] Replace eval() with safe alternative
```

**Inline Comments on Code:**
- Line with API_KEY: "⚠️ Hardcoded secret detected"
- Line with SQL: "⚠️ SQL injection vulnerability"
- Line with eval(): "⚠️ Command injection risk"

---

## 📊 Phase 5: Performance Testing

### Single PR Review Performance

```bash
# Time a single review
START=$(date +%s)

# Create PR (method from Phase 4)
PR_NUMBER=$(gh pr create --title "Perf Test" --body "Test" | grep -oP '\d+$')

# Wait for review
echo "Waiting for agent review..."
sleep 5

# Check if review posted
REVIEWS=$(gh api "/repos/Aries-Serpent/_codex_/pulls/${PR_NUMBER}/reviews" | jq length)

END=$(date +%s)
DURATION=$((END - START))

echo "✅ Review completed in ${DURATION} seconds"
echo "Target: < 30 seconds"

if [ ${DURATION} -lt 30 ]; then
    echo "✅ PASS: Performance target met"
else
    echo "⚠️ WARNING: Performance target not met"
fi
```

### Concurrent PR Testing

```bash
# Create multiple PRs simultaneously
for i in {1..5}; do
    (
        BRANCH="test/concurrent-${i}-$(date +%s)"
        git checkout -b ${BRANCH}
        echo "Test ${i}" > test_${i}.py
        git add test_${i}.py
        git commit -m "Test ${i}"
        git push origin ${BRANCH}
        gh pr create --title "Concurrent Test ${i}" --body "Test" --head ${BRANCH}
    ) &
done

wait

echo "✅ Created 5 concurrent PRs"
echo "Monitor CloudWatch for concurrent execution metrics"
```

### Load Testing

```bash
# Send multiple webhook events
for i in {1..10}; do
    curl -X POST "${WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -H "X-GitHub-Event: ping" \
        -H "X-Hub-Signature-256: sha256=${SIGNATURE}" \
        -d '{"test": true, "index": '${i}'}' &
done

wait

echo "✅ Sent 10 concurrent webhook requests"
```

---

## 📈 Metrics Collection

### CloudWatch Metrics

```bash
# Get Lambda metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=codex-reviewer-agent-dev \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average,Maximum,Minimum

# Get error count
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=codex-reviewer-agent-dev \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum
```

### Custom Metrics from S3

```bash
# Download metrics from S3
aws s3 cp s3://codex-reviewer-metrics-dev/ ./metrics/ --recursive

# Analyze review times
cat metrics/*.json | jq '.review_time_seconds' | \
python3 << 'PYEOF'
import sys
import statistics

times = [float(line.strip()) for line in sys.stdin if line.strip()]
if times:
    print(f"Average: {statistics.mean(times):.2f}s")
    print(f"Median: {statistics.median(times):.2f}s")
    print(f"P95: {sorted(times)[int(len(times)*0.95)]:.2f}s")
    print(f"Max: {max(times):.2f}s")
PYEOF
```

---

## ✅ Test Results Checklist

### Functional Tests
- [ ] Local handler executes successfully
- [ ] Pattern detection works (100% accuracy)
- [ ] Webhook endpoint responds
- [ ] Signature verification works
- [ ] GitHub App installed successfully
- [ ] Agent posts reviews to PRs
- [ ] Inline comments appear correctly
- [ ] Review summary is formatted properly

### Performance Tests
- [ ] Single review < 30 seconds
- [ ] Concurrent reviews handled (5+)
- [ ] No Lambda timeouts
- [ ] API rate limits respected
- [ ] Memory usage < 512MB

### Security Tests
- [ ] Secrets detected correctly
- [ ] SQL injection identified
- [ ] Command injection flagged
- [ ] XSS vulnerabilities caught
- [ ] No false positives on placeholders

### Integration Tests
- [ ] GitHub API calls succeed
- [ ] S3 metrics stored correctly
- [ ] CloudWatch logs populated
- [ ] Error handling works
- [ ] Graceful degradation on API failures

---

## 🐛 Troubleshooting

### Agent Not Responding

```bash
# Check Lambda function status
aws lambda get-function \
    --function-name codex-reviewer-agent-dev

# Check recent invocations
aws lambda get-function-event-invoke-config \
    --function-name codex-reviewer-agent-dev

# View errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/codex-reviewer-agent-dev \
    --filter-pattern "ERROR"
```

### Review Not Posted

```bash
# Check GitHub API rate limits
curl -H "Authorization: Bearer $(gh auth token)" \
     https://api.github.com/rate_limit

# Test API permissions
gh api /repos/Aries-Serpent/_codex_/pulls/1/reviews

# Check Lambda environment variables
aws lambda get-function-configuration \
    --function-name codex-reviewer-agent-dev \
    | jq '.Environment.Variables'
```

### High Latency

```bash
# Check Lambda cold starts
aws logs filter-log-events \
    --log-group-name /aws/lambda/codex-reviewer-agent-dev \
    --filter-pattern "REPORT RequestId" \
    --start-time $(date -d '1 hour ago' +%s)000

# Analyze init duration
# Cold start if "Init Duration" > 0
```

---

## 📊 Success Criteria

### Minimum Acceptable Performance
- ✅ Review time: < 30s (95th percentile)
- ✅ API success rate: > 99%
- ✅ Pattern accuracy: > 95%
- ✅ False positive rate: < 10%
- ✅ Uptime: > 99.9%

### Optimal Performance
- ⭐ Review time: < 15s (median)
- ⭐ API success rate: > 99.9%
- ⭐ Pattern accuracy: 100%
- ⭐ False positive rate: < 5%
- ⭐ Uptime: 100%

---

## 🎯 Next Steps After Testing

1. **If all tests pass:**
   - Deploy to staging
   - Expand to more repositories
   - Monitor for 1 week
   - Deploy to production

2. **If issues found:**
   - Document failures
   - Create bug fixes
   - Retest
   - Iterate

3. **Ongoing monitoring:**
   - Daily metrics review
   - Weekly pattern accuracy check
   - Monthly security audit
   - Quarterly performance optimization

---

**Status:** Ready for execution  
**Estimated Time:** 1-2 hours  
**Prerequisites:** Deployed infrastructure + secrets configured  
**Next:** Execute test phases sequentially
