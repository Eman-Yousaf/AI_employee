# Simple Email Setup (No Google Cloud!)

## The Problem

The Gmail API requires complex setup with Google Cloud Console (credentials, OAuth, verification).

## The Solution: Use IMAP

IMAP is the standard way email clients (like Outlook) connect to Gmail. Much simpler!

---

## Step 1: Enable "Less Secure Apps" OR Create App Password

### Option A: App Password (Recommended)

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google Account
3. Select "Mail" from dropdown
4. Select "Other" and name it "AI Employee"
5. Click "Generate"
6. **Copy the 16-character password** (it looks like: `xxxx xxxx xxxx xxxx`)

### Option B: Allow Less Secure Apps (Not Recommended)

1. Go to https://myaccount.google.com/lesssecureapps
2. Turn it ON

⚠️ **Warning:** This is less secure. Use App Password instead if possible.

---

## Step 2: Create .env File

1. Open Notepad
2. Paste this (replace with your info):

```
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

3. Save as `.env` in the AI_employee folder
4. **Important:** When saving, select "All Files" type, not "Text Files"

---

## Step 3: Test Email Sending

1. Open Command Prompt in AI_employee folder
2. Type:
```
python .claude\skills\gmail-watcher\scripts\gmail_imap.py --vault-path vault
```
3. Check your `vault/Needs_Action/` folder for new emails

---

## That's It!

You can now:
- ✅ Watch Gmail inbox (IMAP version)
- ✅ Send emails (use the SMTP version)

No Google Cloud Console needed!

---

## If App Passwords Don't Work

Some Google accounts don't allow app passwords. In that case:

1. Enable 2-Factor Authentication first
2. Then try app passwords again
3. OR use the "Less Secure Apps" option (temporary)

---

## Alternative: Skip Gmail for Now

Remember, even without Gmail working:
- ✅ **WhatsApp messaging** works
- ✅ **LinkedIn posting** works
- ✅ **Email watching** (IMAP version) works

You can add Gmail API later when you have time to set it up properly!
