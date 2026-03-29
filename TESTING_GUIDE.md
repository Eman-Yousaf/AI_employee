# Testing Guide - Verify Your Setup

## Quick Test Batch Files

I've created batch files to test each service individually or all at once.

---

## Test All at Once

**File:** `Test_All_Setup.bat`

**What it does:**
- Tests Gmail credentials and authentication
- Tests WhatsApp session
- Tests LinkedIn session
- Checks vault folder structure
- Verifies Python dependencies

**When to use:** First time setup, or when something isn't working

**How to use:**
1. Double-click `Test_All_Setup.bat`
2. Follow the prompts
3. See which components pass/fail
4. Follow the fix instructions for any failures

---

## Test Individual Services

### Test Email Only

**File:** `Test_Email_Only.bat`

**What it checks:**
- credentials.json exists
- token.json exists (authenticated)
- Email MCP responds

**When to use:** Email not sending, Gmail issues

**Auto-fix:**
- If not authenticated, automatically runs Gmail_Auth.bat

---

### Test WhatsApp Only

**File:** `Test_WhatsApp_Only.bat`

**What it checks:**
- WhatsApp session exists
- Can connect to WhatsApp Web
- Finds unread messages

**When to use:** WhatsApp not sending messages

**Auto-fix:**
- If no session, opens WhatsApp Web for QR scan

---

### Test LinkedIn Only

**File:** `Test_LinkedIn_Only.bat`

**What it does:**
- Opens browser to test login
- Can generate a test post
- Can post immediately (for testing)

**Options:**
1. **Login test** - Opens browser, you login, session saved
2. **Generate post** - Creates sample post in Pending_Approval/
3. **Post now** - Immediate post to LinkedIn (no approval)

**When to use:** LinkedIn not posting, first-time setup

---

## Quick Reference

| File | Tests | Use When |
|------|-------|----------|
| `Test_All_Setup.bat` | Everything | Initial setup, troubleshooting |
| `Test_Email_Only.bat` | Gmail only | Email issues |
| `Test_WhatsApp_Only.bat` | WhatsApp only | WhatsApp issues |
| `Test_LinkedIn_Only.bat` | LinkedIn only | LinkedIn issues |

---

## Understanding Test Results

### [OK] - Working
Everything is set up correctly!

### [FAIL] - Problem Found
You need to take action. The test will tell you exactly what to do.

### [WARN] - Warning
Might work, but could have issues. Check the details.

### [INFO] - Informational
Just letting you know the status.

---

## Common Test Results & Fixes

### "credentials.json NOT FOUND"
**Fix:**
1. Get credentials.json from Google Cloud Console
2. Put it in config/ folder
3. Run `Gmail_Auth.bat`

### "token.json NOT FOUND"
**Fix:**
1. Run `Gmail_Auth.bat`
2. Login with your Google account
3. Allow permissions

### "WhatsApp session not found"
**Fix:**
1. Run `WhatsApp_Setup.bat`
2. Scan QR code with your phone
3. Session will be saved

### "LinkedIn session not found"
**Fix:**
1. Run `Test_LinkedIn_Only.bat`
2. Choose option 1 (Login test)
3. Login in browser
4. Session will be saved

### "Python not found"
**Fix:**
1. Download Python from https://python.org
2. Install Python 3.10 or higher
3. Check "Add Python to PATH" during install

### "Playwright not installed"
**Fix:**
```
pip install playwright
playwright install chromium
```

---

## Testing Workflow

### First Time Setup:
```
1. Run Test_All_Setup.bat
2. Note which components fail
3. Fix each one:
   - Gmail → Run Gmail_Auth.bat
   - WhatsApp → Run WhatsApp_Setup.bat
   - LinkedIn → Run Test_LinkedIn_Only.bat (option 1)
4. Run Test_All_Setup.bat again
5. All should pass!
```

### Troubleshooting:
```
1. Identify which service isn't working
2. Run specific test (e.g., Test_WhatsApp_Only.bat)
3. Follow fix instructions
4. Test again
5. Working? Great! Still broken? Check error messages
```

---

## Test Before You Start

**Before running `Start_Auto_Processing.bat`, run:**
```
Test_All_Setup.bat
```

This ensures:
- ✅ Gmail ready (or you know it's not set up)
- ✅ WhatsApp ready
- ✅ LinkedIn ready
- ✅ Folders exist
- ✅ Dependencies installed

**Fix any [FAIL] before starting automation!**

---

## Tips

1. **Run Test_All_Setup.bat first** - Know what works and what doesn't
2. **Fix one thing at a time** - Don't try to fix everything at once
3. **Re-run tests after fixes** - Confirm the fix worked
4. **Read the error messages** - They tell you exactly what to do
5. **Check file locations** - Most issues are missing files in wrong places

---

## What Tests Actually Do

### Email Test:
- Looks for `config/credentials.json`
- Looks for `config/token.json`
- Tries to call Email MCP
- Reports if authentication needed

### WhatsApp Test:
- Looks for `whatsapp_session/` folder
- Checks if session has data
- Attempts to connect and check messages
- Reports if QR scan needed

### LinkedIn Test:
- Looks for `vault/.linkedin_session`
- Can open browser to test login
- Can generate sample post
- Can post immediately (test mode)

### Vault Test:
- Checks all required folders exist:
  - Pending_Approval/
  - Approved/
  - Done/
  - Failed/
  - Needs_Action/
  - Plans/

### Dependencies Test:
- Checks Python installed
- Checks Playwright installed
- Checks Google API installed (optional)

---

## Success Looks Like

```
[OK] credentials.json found
[OK] token.json found - Gmail authenticated!
[OK] whatsapp_session found - WhatsApp ready!
[OK] LinkedIn session found - LinkedIn ready!
[OK] All vault folders present
[OK] Python 3.x.x
[OK] Playwright installed
[SUCCESS] All systems ready!
```

**Then you're ready to run `Start_Auto_Processing.bat`!**
