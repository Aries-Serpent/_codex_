# Webhook Registry Integration

**Version:** 1.0.0  
**Last Updated:** 2026-06-20  
**Status:** Active

---

## Overview

The Webhook Registry Integration system enables real-time notification to the Cognitive Brain when registry validations complete. It uses HMAC-SHA256 signed webhooks to ensure secure and verifiable communication.

---

## Webhook Architecture

```
Registry Validation Complete
    ↓
Webhook Notifier
    ├─ Create payload with validation results
    ├─ Sign with HMAC-SHA256
    └─ Send to Cognitive Brain
        ↓
    Cognitive Brain Receives
    ├─ Verify HMAC signature
    ├─ Process validation data
    ├─ Update patterns/learning
    └─ Store for future reference
```

---

## Webhook Payload Structure

### Event: registry_validation_complete

```json
{
  "event": "registry_validation_complete",
  "timestamp": "2026-06-20T09:35:04Z",
  "registry": {
    "type": "ghcr",
    "endpoint": "ghcr.io",
    "namespace": "org/imagename"
  },
  "validation": {
    "confidence": 0.95,
    "valid": true,
    "issues": []
  },
  "connectivity": {
    "overall_status": "passed",
    "tests_summary": {
      "total_tests": 5,
      "passed": 5,
      "failed": 0,
      "success_rate": "100.0%"
    }
  }
}
```

### Payload Fields

#### Top-Level Fields
- `event` (string): Event type ("registry_validation_complete")
- `timestamp` (ISO 8601): UTC timestamp of event
- `registry` (object): Registry configuration
- `validation` (object): Validation results
- `connectivity` (object, optional): Connectivity test results

#### Registry Object
- `type` (string): Registry type (dockerhub, ghcr, private, ecr, gcr)
- `endpoint` (string): Registry endpoint URL
- `namespace` (string): Registry namespace/organization

#### Validation Object
- `confidence` (number): Confidence score (0.0-1.0)
- `valid` (boolean): Configuration is valid
- `issues` (array): List of validation issues

#### Connectivity Object (Optional)
- `overall_status` (string): "passed" or "failed"
- `tests_summary` (object):
  - `total_tests` (number): Total connectivity tests
  - `passed` (number): Tests that passed
  - `failed` (number): Tests that failed
  - `success_rate` (string): Percentage success

---

## Webhook Headers

All webhook requests include:

```
Content-Type: application/json
X-Webhook-Event: registry_validation_complete
X-Webhook-Signature: sha256=<hmac-sha256-signature>
```

### HMAC-SHA256 Signature

**Algorithm:**
1. Serialize payload to JSON (sorted keys)
2. Generate HMAC-SHA256 hash using webhook secret
3. Prepend "sha256=" to hexdigest
4. Add to X-Webhook-Signature header

**Verification Example (Python):**
```python
import hashlib
import hmac

def verify_signature(payload_json, signature, secret):
    # Extract signature from header: "sha256=<hex>"
    expected_sig = "sha256=" + hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)
```

---

## Security Considerations

### Webhook Secret Management

**Storage:**
- Store webhook secret in GitHub Secrets
- Reference as `${{ secrets.WEBHOOK_SECRET }}`
- Rotate secrets quarterly
- Never commit secrets to repository

**Access Control:**
- Webhook secret visible only to repository admins
- Use separate secrets for different environments
- Audit secret access and rotation

### Signature Verification

**Always verify webhook signature:**
```python
@app.route('/webhook/registry', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.get_data()

    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        abort(401)  # Unauthorized

    # Process webhook
    data = json.loads(payload)
    return "OK", 200
```

### Network Security
- Use HTTPS only for webhook endpoint
- Validate webhook URL before deployment
- Implement rate limiting on webhook endpoint
- Log all webhook deliveries

---

## Webhook Configuration

### GitHub Secrets Setup

```bash
# Set webhook URL
gh secret set COGNITIVE_BRAIN_WEBHOOK_URL -b "https://brain.example.com/webhook"

# Set webhook secret
gh secret set WEBHOOK_SECRET -b "your-secret-key-here"
```

### Webhook Endpoint Setup

Your Cognitive Brain should expose an HTTP endpoint:

```
POST /webhook/registry
```

**Expected Response:**
```
HTTP 200 OK
```

### Retry Policy

- Initial attempt on workflow completion
- Automatic retries: 3 attempts
- Retry delay: 5 seconds between attempts
- Timeout: 10 seconds per request

---

## Webhook Events

### Event: registry_validation_complete

**Triggered:** After registry validation and connectivity testing  
**Payload:** Full validation and connectivity results  
**Handler:** `POST /webhook/registry`

**Example Scenarios:**
- ✅ Valid configuration, all connectivity tests pass
- ⚠️ Valid configuration, some connectivity tests fail
- ❌ Invalid configuration, validation fails
- ⚠️ Configuration cannot be validated (service unavailable)

---

## Repository Variables

### Variables Stored by Workflow

After successful webhook notification, these variables are available:

```yaml
REGISTRY_TYPE: "ghcr"                    # Registry type
REGISTRY_ENDPOINT: "ghcr.io"             # Registry endpoint
REGISTRY_NAMESPACE: "org/imagename"      # Namespace
REGISTRY_VALIDATION_STATUS: "valid"      # Validation status
REGISTRY_LAST_VALIDATED: "2026-06-20..." # Last validation timestamp
```

### Using Variables in Workflows

```yaml
- name: Use registry variables
  env:
    REGISTRY_TYPE: ${{ vars.REGISTRY_TYPE }}
    REGISTRY_ENDPOINT: ${{ vars.REGISTRY_ENDPOINT }}
  run: |
    echo "Using $REGISTRY_TYPE registry at $REGISTRY_ENDPOINT"
```

### Updating Variables via CLI

```bash
# Set variable
gh variable set REGISTRY_TYPE --body "ghcr"

# Get variable
gh variable get REGISTRY_TYPE

# List all variables
gh variable list

# Delete variable
gh variable delete REGISTRY_TYPE
```

---

## Webhook Validation Report

The webhook validation includes:

```json
{
  "validation_report": {
    "webhook_configured": true,
    "hmac_signature_enabled": true,
    "payload_structure": "valid",
    "ready_for_delivery": true
  }
}
```

### Validation Checks
- ✅ Webhook URL configured
- ✅ HMAC signature enabled
- ✅ Payload structure valid
- ✅ Ready for delivery

---

## Testing Webhook Integration

### Step 1: Generate Test Payload

```bash
python scripts/webhook/notify_brain.py > webhook_test_payload.json
```

### Step 2: Verify Signature

```bash
# Extract signature from payload
SIGNATURE=$(jq -r '.headers."X-Webhook-Signature"' webhook_test_payload.json)

# Regenerate signature locally
PAYLOAD=$(jq '.webhook_notification.payload' webhook_test_payload.json -c)
EXPECTED=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "test_secret_key" -hex | cut -d' ' -f2)

# Compare
[ "$SIGNATURE" == "sha256=$EXPECTED" ] && echo "Signature valid" || echo "Signature invalid"
```

### Step 3: Test Delivery

```bash
# Send test webhook
PAYLOAD=$(jq '.webhook_notification.payload' webhook_test_payload.json -c)
SIGNATURE=$(jq -r '.headers."X-Webhook-Signature"' webhook_test_payload.json)

curl -X POST https://brain.example.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Event: registry_validation_complete" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

---

## Cognitive Brain Integration

### Pattern Learning from Webhooks

When Cognitive Brain receives webhook notification:

1. **Validate signature** - Ensure authenticity
2. **Parse payload** - Extract registry and validation data
3. **Update patterns** - Integrate results into knowledge base
4. **Learn from validation** - Improve confidence scoring
5. **Store metadata** - Persist for future queries

### Pattern Refinement

Over time, the system learns:
- Which configuration patterns work
- Registry-specific best practices
- Common validation failures
- Trends in connectivity issues

---

## Troubleshooting

### Webhook Not Received

**Possible Causes:**
- Webhook URL not configured
- Endpoint not accessible
- Firewall blocking requests
- Invalid webhook secret

**Solution:**
1. Verify webhook URL: `gh secret list | grep WEBHOOK_URL`
2. Test endpoint: `curl -I https://endpoint/webhook`
3. Check firewall rules
4. Verify secret is set correctly

### Signature Verification Fails

**Possible Causes:**
- Secret mismatch
- Payload modified
- Encoding issues

**Solution:**
1. Verify secret matches: `gh secret list`
2. Ensure payload not modified in transit
3. Check JSON encoding (should be UTF-8)
4. Regenerate test with correct secret

### Webhook Delivery Timeout

**Possible Causes:**
- Endpoint slow to respond
- Network latency
- Cognitive Brain overloaded

**Solution:**
1. Optimize endpoint response time
2. Check network connectivity
3. Monitor Cognitive Brain resources
4. Consider async webhook processing

---

## Best Practices

### Webhook Configuration
- ✅ Use strong, random webhook secrets
- ✅ Rotate secrets quarterly
- ✅ Use HTTPS for all webhook URLs
- ✅ Validate signatures on receipt
- ✅ Log all webhook events

### Error Handling
- ✅ Implement exponential backoff for retries
- ✅ Log delivery failures with details
- ✅ Alert on repeated failures
- ✅ Implement dead-letter queue for failed deliveries

### Monitoring
- ✅ Track webhook delivery success rate
- ✅ Monitor payload processing time
- ✅ Alert on signature verification failures
- ✅ Track pattern learning progress

---

## Maintenance & Updates

**Last Updated:** 2026-06-20  
**Review Frequency:** Quarterly  
**Next Review:** 2026-09-20

**Maintainer:** Cognitive Brain Registry Team  
**Escalation:** @mbaetiong
