# Fix Gmail 403 Error

## What This Error Means

The error `403: access_denied` means your Gmail app needs to be configured properly in Google Cloud Console.

## Quick Fix (2 Options)

---

## Option 1: Add Yourself as Test User (Easiest)

1. Go to https://console.cloud.google.com
2. Select your project
3. Go to "APIs & Services" → "OAuth consent screen"
4. Scroll down to "Test users"
5. Click "Add users"
6. Enter your Gmail address
7. Click "Save"
8. Try `Gmail_Auth.bat` again

---

## Option 2: Make App Internal (If Using Workspace)

1. Go to https://console.cloud.google.com
2. "OAuth consent screen"
3. Change "User Type" from "External" to "Internal"
4. Save
5. Try `Gmail_Auth.bat` again

---

## Option 3: Skip Gmail for Now (WhatsApp & LinkedIn Still Work)

If Gmail setup is too complicated, you can still use:
- ✅ **WhatsApp messaging** (no Google needed)
- ✅ **LinkedIn posting** (no Google needed)
- ✅ **Gmail watching** (IMAP instead of API - see below)

---

## Alternative: Use IMAP Instead of Gmail API

I've created a simpler Gmail watcher that uses IMAP (your regular email login) instead of the complex Gmail API.

### To use IMAP:

1. Open your email settings
2. Enable "Less secure app access" or create an "App Password"
3. Use your email and password directly

This avoids all the Google Cloud Console setup!

---

## Complete Step-by-Step Fix

### Step 1: Open Google Cloud Console

Go to: https://console.cloud.google.com

### Step 2: Select Your Project

Click the project dropdown at the top and select your AI Employee project

### Step 3: Go to OAuth Consent Screen

1. Click the hamburger menu (☰)
2. Go to "APIs & Services"
3. Click "OAuth consent screen"

### Step 4: Add Test User

1. Scroll to "Test users" section
2. Click "+ Add users"
3. Type your Gmail address
4. Click "Add"

### Step 5: Try Again

Run `Gmail_Auth.bat` again

---

## Still Not Working?

Try this alternative authentication:

### Using App Password (Recommended)

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google Account
3. Select "Mail" and your device
4. Click "Generate"
5. Copy the 16-character password
6. I will create a simple config file for you

This is much simpler than OAuth!

---

## Common Causes

| Cause | Solution |
|-------|----------|
| App not verified | Add yourself as test user |
| Wrong project | Select correct project in dropdown |
| OAuth screen not published | Click "Publish app" button |
| Wrong email | Use same email as test user |

---

## Need More Help?

The error is because Google requires verification for apps that access Gmail. While you're testing, adding yourself as a "Test user" is the easiest fix.

**Remember:** Even without Gmail API working, you can still:
- Send WhatsApp messages
- Post to LinkedIn
- Use IMAP to check email (alternative)

Don't let this block you! The other features work independently.
