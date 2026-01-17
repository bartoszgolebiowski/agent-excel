# 🚀 Quick Start Guide - Email Processing System

## ⏱️ 5-Minute Setup

### Step 1: Clone & Navigate

```bash
cd agent-excel
```

### Step 2: Install Dependencies

```bash
pip install -e .
```

### Step 3: Configure API Key

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:

   ```env
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   ```

   > 💡 Get a free API key at [openrouter.ai](https://openrouter.ai)

### Step 4: Run the System

```bash
python src/main.py
```

That's it! The system will:

- ✅ Find 3 sample emails in `data/inbox/`
- ✅ Analyze each with AI
- ✅ Save results to `data/email_report.xlsx`
- ✅ Move processed files to `data/archive/`

---

## 📋 What You'll See

**Console Output:**

```
============================================================
INTELLIGENT CORRESPONDENCE ASSISTANT - SINGLE RUN
============================================================

============================================================
Email Processing Cycle - 2026-01-17 10:30:00
============================================================

  → Executing: Checking inbox folder for new emails
  → Analyzing email with AI...
  → Executing: Saving email analysis to Excel report
  → Executing: Moving processed email to archive folder
  → Analyzing email with AI...
  → Executing: Saving email analysis to Excel report
  → Executing: Moving processed email to archive folder
  → Analyzing email with AI...
  → Executing: Saving email analysis to Excel report
  → Executing: Moving processed email to archive folder

✓ Cycle completed: All 3 emails processed

============================================================
Cycle Summary: 3 email(s) processed
============================================================
```

**Excel Output (`data/email_report.xlsx`):**

| Main Topic    | Business Category | Contact Data              | Urgency | Sentiment | Summary                                                   | Event Date          | Source File   |
| ------------- | ----------------- | ------------------------- | ------- | --------- | --------------------------------------------------------- | ------------------- | ------------- |
| System Down   | Tech Support      | sarah.johnson@company.com | High    | Negative  | Authentication service unavailable, blocking presentation | 2026-01-17T10:30:00 | email_001.txt |
| Quote Request | Sales             | m.chen@techcorp.com       | Medium  | Neutral   | Enterprise package quote for 50 users requested           | 2026-01-17T10:31:00 | email_002.txt |
| Invoice Error | Accounting        | lisa.m@clientco.com       | Medium  | Neutral   | Invoice charged $500 more than quoted amount              | 2026-01-17T10:32:00 | email_003.txt |

**File Structure After:**

```
data/
├── inbox/               (empty - all processed)
├── archive/
│   ├── email_001.txt   ← Moved here
│   ├── email_002.txt   ← Moved here
│   └── email_003.txt   ← Moved here
└── email_report.xlsx   ← Created with 3 rows
```

---

## 🔄 Enable Cyclic Mode (Optional)

To run continuously (e.g., every hour):

1. Edit `.env`:

   ```env
   CYCLIC_MODE=true
   CYCLE_INTERVAL_SECONDS=3600  # 1 hour
   ```

2. Run:

   ```bash
   python src/main.py
   ```

3. The system will now:
   - Process all emails in inbox
   - Wait 1 hour
   - Check again for new emails
   - Repeat forever (Ctrl+C to stop)

**Use Cases:**

- 📧 Monitor a shared email inbox
- 📁 Process files dropped by another system
- ⏰ Daily/hourly batch processing

---

## 📝 Adding Your Own Emails

### Format

Create `.txt` files in `data/inbox/` with email content:

```
Subject: Your Subject Here

Email body goes here...
Multiple lines are fine.

Contact info:
email@example.com
+1-555-1234
```

### Example Email Types

**Support Ticket:**

```
Subject: Application Crashes on Startup

Hi Support,

Our app crashes immediately after opening. Error code: 0x80004005.
This is blocking our entire team - please help ASAP!

John Doe
john@company.com
```

**Sales Inquiry:**

```
Subject: Pricing for 100 Licenses

Hello,

We're interested in purchasing 100 licenses for our organization.
Could you send pricing and volume discounts?

Thank you,
Mary Smith
mary@bigcorp.com
```

**Complaint:**

```
Subject: Very disappointed with service

I've been waiting 3 weeks for a response to my ticket #12345.
This is completely unacceptable! I'm considering switching providers.

- Angry Customer
```

---

## 🛠️ Customization

### Change Categories

Edit `src/prompting/jinja/skills/analyze_email.j2`:

```jinja
2. **Business Category**: Assign the email to:
   - Sales
   - HR
   - Tech Support
   - Accounting
   - Customer Service
   - Billing          ← Add your category
   - Other
```

### Change Output Path

Edit `.env`:

```env
EXCEL_PATH=C:/Reports/emails.xlsx  # Custom path
```

### Change Analysis Criteria

Edit `src/prompting/jinja/skills/analyze_email.j2`:

```jinja
4. **Urgency**: Assess the urgency level based on:
   - **Critical**: System outage, security breach
   - **High**: Contains keywords like "ASAP", "urgent"
   - **Medium**: Mentions deadlines within 7 days
   - **Low**: General inquiry
```

---

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_email_system.py
```

This checks:

- ✅ Sample emails exist
- ✅ API key is configured
- ✅ Agent initializes correctly
- ✅ Processing completes successfully
- ✅ Excel file is created
- ✅ Files are archived

---

## 🐛 Common Issues

### "No API key configured"

**Problem:** `.env` file missing or no `OPENROUTER_API_KEY` set

**Solution:**

```bash
cp .env.example .env
# Edit .env and add: OPENROUTER_API_KEY=your_key_here
```

### "Import openpyxl could not be resolved"

**Problem:** Dependency not installed

**Solution:**

```bash
pip install openpyxl
# or
pip install -e .
```

### "FileNotFoundError: Email file not found"

**Problem:** Inbox path incorrect or files moved during processing

**Solution:**

- Check `INBOX_PATH` in `.env`
- Ensure path exists: `mkdir -p data/inbox`
- Verify files haven't already been processed

### Excel file is locked

**Problem:** Excel is open while agent tries to write

**Solution:**

- Close Excel before running
- Or change `EXCEL_PATH` to a different file

---

## 📚 Next Steps

1. **Read the full docs:** [EMAIL_ASSISTANT_README.md](EMAIL_ASSISTANT_README.md)
2. **Understand the workflow:** [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)
3. **Explore the code:** Start with `src/main.py` → `src/agent.py`
4. **Customize prompts:** Edit `src/prompting/jinja/skills/analyze_email.j2`
5. **Add features:** Follow patterns in `.github/copilot-instructions.md`

---

## 💡 Tips

- **Test with small batches first:** Start with 1-3 emails to verify behavior
- **Monitor the console:** Watch for errors or unexpected behavior
- **Check the Excel file:** Verify data extraction is accurate
- **Iterate on prompts:** Adjust `analyze_email.j2` based on your email types
- **Use version control:** Git commit before making changes

---

## 🤝 Need Help?

1. Check [EMAIL_ASSISTANT_README.md](EMAIL_ASSISTANT_README.md) - Full documentation
2. Review [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) - Technical details
3. Read [.github/copilot-instructions.md](.github/copilot-instructions.md) - Architecture guide

---

**Happy Processing! 🎉**
