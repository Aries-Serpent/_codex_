## Getting Started Guide for End Users & Business Users
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-07-08
**Target Audience:** Business analysts, non-technical users, decision makers, SMEs
**Estimated Time:** 10 minutes to first prediction

## Your Goal

Use pre-trained models through web interfaces, no coding required. Make predictions, track results, and export insights for business decisions.

---

## Phase 1: Web Dashboard Access (2 minutes)

## Getting Started

**Visit:** https://app.codex-ml.dev

**Sign Up:**
1. Click "Sign Up" button
2. Enter email and create password
3. Verify email (check spam folder if needed)
4. You're ready!

**Sign In:**
- Email: your.email@company.com
- Password: (securely stored)
- Optional: Enable two-factor authentication (2FA)

---

## Phase 2: Making Your First Prediction (5 minutes)

### Step 1: Choose a Model

1. **Go to Models** You'll see available pre-trained models:
 - Sentiment Analyzer
 - Text Classifier
 - Anomaly Detector
 - And more...

2. **Click a Model** to view details:
 - What it does (description)
 - Example inputs/outputs
 - Accuracy and performance metrics
 - How to use it

### Step 2: Make a Prediction

**Option A: Single Prediction**

1. Click "Try It Out"
2. Enter text or upload data:
 ```
 Input: "I love this product!"
 ```
3. Click "Predict"
4. See instant result:
 ```
 Sentiment: POSITIVE
 Confidence: 95%
 ```

**Option B: Batch Upload**

1. Click "Upload File"
2. Upload CSV file:
 ```
 text,category
 "Great product!",product_review
 "Terrible experience.",product_review
 ```
3. Click "Process"
4. Results display in table format
5. Download results as CSV or Excel

### Step 3: View & Save Results

**Results Dashboard:**
- See all predictions in one place
- Filter by date, confidence, category
- Export to Excel, PDF, or CSV
- Print or share with team

**Save for Later:**
- Click ⭐ to save interesting results
- Access saved results under "My Saved Predictions"
- Create folders to organize by project

---

## Phase 3: Common Use Cases

### Use Case 1: Customer Feedback Analysis

**Scenario:** Analyze 1000+ customer reviews monthly

**Steps:**
1. Collect reviews in Excel/CSV
2. Go to Sentiment Analyzer
3. Upload your file (customer_feedback.csv)
4. Wait 2-3 minutes for processing
5. Download results
6. Share sentiment summary with leadership

**Result:**
```
 1000 reviews processed
 78% positive sentiment
 15% negative sentiment 
 7% neutral
 Share dashboard link with team
```

### Use Case 2: Content Categorization

**Scenario:** Organize support tickets by topic

**Steps:**
1. Export tickets from support system
2. Use Text Classifier model
3. Upload ticket data
4. Receive automatic categorization
5. Route tickets to correct teams

**Result:**
```
 Billing Issues: 245 tickets
 Technical Support: 428 tickets
 Feature Requests: 187 tickets
 Auto-route to teams
```

### Use Case 3: Quality Control

**Scenario:** Flag potentially defective products

**Steps:**
1. Upload product descriptions
2. Use Anomaly Detector
3. Flag unusual/suspicious items
4. Manual review queue appears
5. Review flagged items
6. Take action

**Result:**
```
 5000 products scanned
 12 anomalies detected
 Manual review queue ready
 QA team investigates
```

---

## Phase 4: Sharing & Collaboration

### Share Results with Team

**Create Report:**
1. Go to Results "Share"
2. Select predictions to include
3. Choose report format:
 - Dashboard (interactive)
 - PDF (printable)
 - PowerPoint (presentation)
4. Enter recipient emails
5. Click "Send"

**Share Dashboard Link:**
1. Results "Generate Link"
2. Copy link
3. Send to team
4. Recipients can view (read-only)

### Create Alerts

**Get Notified Automatically:**
1. Settings Alerts
2. "New Alert"
3. Choose trigger:
 - When prediction changes significantly
 - New high-confidence predictions
 - Weekly summary email
4. Set frequency (daily, weekly, monthly)
5. Choose recipients
6. Save

**Example:**
```
Alert: Daily Sentiment Summary
 Send to: team@company.com
 Time: 9:00 AM daily
 Include: Sentiment trends, top issues
```

---

## Phase 5: Best Practices & Tips

### Do's

- **Prepare clean data**: Remove extra spaces, fix formatting
- **Check confidence scores**: High confidence (>90%) = more reliable
- **Validate results**: Sample-check predictions manually
- **Document patterns**: Note when model performs well/poorly
- **Use consistently**: Same model for trending over time
- **Save important results**: Use star/folder feature
- **Ask for help**: Click "?" on any page for assistance

### Don'ts

- **Don't trust 100%**: All models make mistakes sometimes
- **Don't upload sensitive data**: PII, financial info, etc.
- **Don't ignore low confidence**: Results <60% confidence may be uncertain
- **Don't mix data types**: Keep text input separate from numeric
- **Don't edit raw results**: Keep original for audit trail
- **Don't process identical data repeatedly**: Use saved results instead

### Pro Tips

**Tip 1: Batch Processing is Faster**
- Processing 1 item: 1-2 seconds
- Processing 100 items: 5-10 seconds (0.05-0.1 seconds per item)
- **Save time by uploading batches**

**Tip 2: Look for Confidence Scores**
```
 95% confidence = Very reliable
 70% confidence = Generally reliable
 50% confidence = Be cautious
```

**Tip 3: Export for Excel**
1. Click "Download" button
2. Choose "Excel with formatting"
3. Results arrive formatted & ready to share

**Tip 4: Set Up Recurring Batches**
- Process same data weekly/monthly
- Schedule in Settings Automation
- Results auto-download

---

## Phase 6: Troubleshooting

### Issue: "Upload Failed"

**Causes & Solutions:**
- File too large (>100MB) Split into smaller files
- Wrong format (PDF) Convert to CSV/Excel
- Missing headers Add column names to first row
- Special characters Remove or replace

**How to fix:**
```
 customer_reviews.pdf Download as CSV
 data.txt (no headers) Add headers: text, date, category
 huge_file_500mb.csv Split into 5 files of 100mb each
 feedback.csv Ready to upload
```

### Issue: "Predictions Look Wrong"

**Possible reasons:**
- Model doesn't understand your domain
- Data is different from training data
- Confidence score is low
- Edge case or exception

**What to do:**
1. Check confidence score
 - Low (<60%) Results uncertain
 - High (>80%) Check input format
2. Manual validation
 - Review 10-20 random predictions
 - Compare with your knowledge
3. Ask for help
 - Contact support team
 - Share 3-5 examples

### Issue: "How Long Does Processing Take?"

**Processing times:**
- Single prediction: 1-2 seconds
- 100 items: 5-10 seconds
- 1000 items: 1-2 minutes
- 10000 items: 10-20 minutes

**Large batch tips:**
- Upload during off-peak hours
- Process overnight if > 50,000 items
- Break into smaller files if needed

---

## Phase 7: Getting Help

### Learning Resources

- **Video Tutorials**: [YouTube Channel](https://youtube.com/codex-ml)
 - 2-5 minute walkthroughs
 - Common use cases covered
 - No technical knowledge needed

- **Help Center**: [help.codex-ml.dev](https://help.codex-ml.dev)
 - FAQs by topic
 - Video guides
 - Searchable knowledge base

- **Live Chat**: In app (bottom right corner)
 - Available 9 AM - 5 PM (PT)
 - Average response: 2 minutes
 - Multilingual support

### 🆘 Support Options

**Quick Issues:**
- Click "?" icon anywhere in app
- Scroll through FAQ section
- Most questions answered in 1 minute

**Detailed Help:**
- Click "Help" "Contact Support"
- Describe your issue
- Attach screenshots if helpful
- Get response within 24 hours

**Video Demos:**
- Visit Help Center
- Click "Video Tutorials"
- Find your use case
- Follow along step-by-step

---

## Phase 8: Account & Security

### Account Settings

**Change Password:**
1. Settings Security Change Password
2. Enter current password
3. Enter new password (8+ characters, mix of letters/numbers)
4. Confirm new password
5. Click "Update"

**Enable Two-Factor Authentication:**
1. Settings Security Two-Factor Auth
2. Choose method:
 - Authenticator App (Google Authenticator, Authy)
 - Email codes
3. Follow setup instructions
4. Save backup codes (in case phone lost)

**View Account Activity:**
1. Settings Security Activity Log
2. See all logins and password changes
3. If unfamiliar activity, click "Change Password" immediately

### Data Privacy

**Your Data:**
- Your predictions are private
- We don't share your data with others
- You can delete all data anytime
- GDPR/CCPA compliant

**Download Your Data:**
1. Settings Data "Download My Data"
2. Receive email with all your data
3. Can import to another system

**Delete Your Account:**
1. Settings Account "Delete Account"
2. Confirm deletion
3. All data permanently deleted
4. Cannot be undone

---

## Next Steps

1. **Explore Models**: Try 2-3 different models with sample data
2. **Do a Pilot**: Use with small dataset (10-100 items)
3. **Get Team Input**: Share results with colleagues
4. **Scale Up**: Process full batch when confident
5. **Automate**: Set up weekly/monthly recurring tasks
6. **Measure Impact**: Track how predictions helped decisions

## FAQ - Frequently Asked Questions

**Q: Is my data safe?**
A: Yes! Data is encrypted in transit and at rest. We never share your data with third parties.

**Q: What file formats work?**
A: CSV, Excel (.xlsx), Text. Maximum 100MB per upload.

**Q: How accurate are predictions?**
A: Most models 85-95% accurate on typical data. Check confidence scores - they tell you reliability.

**Q: Can I download results?**
A: Yes! Export as CSV, Excel, or PDF anytime.

**Q: Is there a free trial?**
A: Yes! $0 to start. Upgrade only when ready.

---

**Welcome to Codex ML! Start predicting today **
