# Share on GitHub - Privacy Protection Guide

## What You MUST Keep Private

These files contain your personal credentials - NEVER share them:

```
config/credentials.json          ← Gmail API credentials
config/token.json                ← Gmail login token
.env                             ← Email/passwords
whatsapp_session/                ← WhatsApp login session
vault/.linkedin_session/         ← LinkedIn login session
vault/.whatsapp_processed.json   ← WhatsApp data
```

---

## Step 1: Check .gitignore

Your project already has a `.gitignore` file. Make sure it includes:

```
# Credentials - NEVER SHARE
config/credentials.json
config/token.json
.env
.env.local

# Sessions - NEVER SHARE
whatsapp_session/
linkedin_session/
vault/.linkedin_session/
vault/.whatsapp_session/
vault/.whatsapp_processed.json

# Logs (may contain private data)
*.log
Logs/

# Python cache
__pycache__/
*.pyc
*.pyo
```

**Verify it's working:**
```bash
git status
```
You should NOT see credentials.json or token.json listed.

---

## Step 2: Remove Private Data Before Sharing

### Delete these files/folders (keep backups locally!):

```bash
# Remove credentials (keep local copies!)
rm config/credentials.json
rm config/token.json
rm .env

# Remove sessions (keep local copies!)
rm -rf whatsapp_session/
rm -rf vault/.linkedin_session/
rm vault/.whatsapp_processed.json

# Remove logs
rm -rf vault/Logs/*
rm orchestrator.log
```

---

## Step 3: Create Template Files

Create safe template versions for others to use:

### config/credentials.json.template
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID_HERE",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET_HERE",
    "redirect_uris": ["http://localhost"]
  }
}
```

### .env.template
```
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
VAULT_PATH=./vault
```

---

## Step 4: Add README Instructions

Update README.md with setup instructions:

```markdown
## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/AI_employee.git
```

### 2. Install dependencies
```bash
pip install playwright google-api-python-client
playwright install chromium
```

### 3. Configure Gmail (for email sending)
1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API
3. Download credentials.json
4. Put in config/ folder
5. Run Gmail_Auth.bat

### 4. Configure WhatsApp
1. Run WhatsApp_Setup.bat
2. Scan QR code with phone

### 5. Configure LinkedIn
1. Run Test_LinkedIn_Only.bat
2. Login in browser

### 6. Start automation
Run Start_Auto_Processing.bat
```

---

## Step 5: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to https://github.com
2. Click "+" → "New repository"
3. Name: `AI_employee`
4. Choose: Public or Private
5. Click "Create repository"
6. Follow the instructions to push your code

### Option B: Using Git Commands

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Employee Silver Tier"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/AI_employee.git
git branch -M main
git push -u origin main
```

---

## Step 6: Verify Nothing Private Leaked

After pushing to GitHub, check:

1. Go to your repo on GitHub
2. Browse files
3. Make sure these are NOT visible:
   - ❌ config/credentials.json
   - ❌ config/token.json
   - ❌ .env
   - ❌ whatsapp_session/ folder
   - ❌ Any .log files
   - ❌ vault/.linkedin_session/

4. Check commit history doesn't show private data:
   ```bash
   git log --all --full-history -- "config/credentials.json"
   ```

---

## What To Include (Safe to Share)

```
✅ All .bat files (they don't contain credentials)
✅ All .py scripts (they read credentials from files)
✅ All .md guides (documentation)
✅ vault/Templates/ (templates, not data)
✅ .claude/skills/ (automation code)
✅ orchestrator.py (main script)
✅ scripts/ (helper scripts)
✅ README.md (with setup instructions)
✅ .gitignore (privacy protection)

✅ vault/ folder structure (but not the session files)
   - vault/Pending_Approval/ (can be empty)
   - vault/Approved/ (can be empty)
   - vault/Done/ (can be empty)
   - etc.
```

---

## Quick Checklist Before Pushing

- [ ] config/credentials.json is in .gitignore
- [ ] config/token.json is in .gitignore
- [ ] .env is in .gitignore
- [ ] whatsapp_session/ is in .gitignore
- [ ] .linkedin_session/ is in .gitignore
- [ ] Removed actual credentials (keep backups locally)
- [ ] Created template files (.template)
- [ ] Updated README with setup instructions
- [ ] Tested git status - no private files shown
- [ ] Checked GitHub repo after push - no private files visible

---

## If You Accidentally Shared Private Data

### Remove from Git history:
```bash
# Remove file from all history
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch config/credentials.json' \
--prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### Or safer - delete and recreate repo:
1. Delete GitHub repository
2. Create new one
3. Clean local files
4. Push clean version

**Also revoke credentials:**
- Google Cloud Console → Delete OAuth credentials
- WhatsApp → Log out all devices
- LinkedIn → Change password

---

## Summary

**KEEP PRIVATE (never share):**
- config/credentials.json
- config/token.json
- .env
- whatsapp_session/
- .linkedin_session/

**SHARE SAFELY (the project code):**
- All .bat files
- All .py scripts
- vault/ folder structure (empty)
- Templates/
- Documentation

**Your data is separate from your code!**
