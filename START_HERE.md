# AI Employee - Silver Tier
## Complete Setup Guide for Beginners

---

## What Is This?

This is an **AI Employee** that automates your business tasks:
- **Sends emails** through Gmail
- **Sends WhatsApp messages**
- **Posts on LinkedIn** for your business
- **Monitors your Gmail inbox** for important emails
- **Creates action plans** from messages

**You control everything from Obsidian** - a simple note-taking app.

---

## What You Need Before Starting

1. **Obsidian app** installed on your computer
   - Download from: https://obsidian.md

2. **Gmail account** (to send emails)

3. **WhatsApp** on your phone (to send messages)

4. **LinkedIn account** (to post business updates)

---

## Folder Structure (What Each Folder Does)

```
AI_employee/
│
├── START_HERE.md              ← You are here!
├── GETTING_STARTED.md         ← Detailed guide
├── orchestrator.py            ← The brain (don't touch)
│
├── Start_Auto_Processing.bat  ← RUN THIS FIRST
├── Execute_Approved.bat       ← Run manually if needed
├── Gmail_Auth.bat            ← Gmail setup (one time)
│
├── config/                    ← Gmail credentials
│   └── credentials.json       ← From Google Cloud
│
├── scripts/                   ← Helper scripts
│   └── mcp_email_client.py   ← Email sender
│
├── .claude/skills/           ← Automation scripts
│   ├── gmail-watcher/        ← Watches Gmail
│   ├── whatsapp-watcher/     ← Watches WhatsApp
│   ├── linkedin-poster/      ← Posts to LinkedIn
│   └── approval-workflow/     ← Processes approvals
│
└── vault/                     ← YOUR OBSIDIAN VAULT
    ├── Pending_Approval/      ← Draft emails/messages
    ├── Approved/              ← Ready to send
    ├── Done/                  ← Successfully sent
    ├── Failed/                ← Errors
    ├── Needs_Action/          ← New items from Gmail
    ├── Plans/                 ← Your action plans
    ├── Dashboard.md           ← See status here
    └── Templates/             ← Copy-paste templates
```

---

## Step-by-Step Setup

### STEP 1: Install Obsidian

1. Go to https://obsidian.md
2. Download for Windows
3. Install it
4. Open Obsidian

### STEP 2: Open This Vault in Obsidian

1. In Obsidian, click "Open folder as vault"
2. Navigate to: `Documents/GitHub/AI_employee/vault`
3. Select it and open

### STEP 3: Set Up Gmail (Required for Email)

**You need a file called `credentials.json` from Google Cloud Console.**

If you don't have it yet:
1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Gmail API
4. Create OAuth credentials
5. Download `credentials.json`
6. Put it in the `config/` folder

Then:
1. Double-click `Gmail_Auth.bat`
2. Follow the login process
3. You'll get a `token.json` file
4. Now you can send emails!

### STEP 4: Start the Automation

1. Double-click `Start_Auto_Processing.bat`
2. A black window opens
3. Press any key
4. Minimize the window (don't close it!)
5. ✅ Automation is now running

### STEP 5: Send Your First Email

1. In Obsidian, open `Pending_Approval/` folder
2. Create new note (Ctrl+N)
3. Name it: `test_email`
4. Copy this:

```markdown
---
action: send_email
to: "your-email@gmail.com"
subject: "Test"
priority: medium
---

Hello! This is a test.
```

5. Save (Ctrl+S)
6. Drag file to `Approved/` folder
7. Wait 60 seconds
8. Check your email!

---

## How It Works (Simple Explanation)

### The Process:

1. **You create** a file in `Pending_Approval/` with email/message details
2. **You review** and drag to `Approved/`
3. **Automation detects** the file in `Approved/`
4. **Automation sends** the email/message
5. **Automation moves** file to `Done/`

### Why This Way?

- **Safety**: You review everything before sending
- **Control**: Nothing sends without your approval
- **Record**: Everything is saved in `Done/` for history

---

## Daily Use

### To Send an Email:

1. Create file in `Pending_Approval/`
2. Use this format:

```markdown
---
action: send_email
to: "recipient@example.com"
subject: "Subject line"
priority: medium
---

Your email body here.
```

3. Drag to `Approved/`
4. Done!

### To Send WhatsApp:

```markdown
---
action: send_whatsapp
chat_name: "Exact Contact Name"
priority: medium
---

Your message here.
```

### To Post LinkedIn:

```markdown
---
action: social_post
platform: linkedin
---

Your post content here.

#hashtag1 #hashtag2
```

---

## Troubleshooting

### "Nothing is sending"

Check:
1. Is `Start_Auto_Processing.bat` running? (black window open)
2. Is file in `Approved/` folder?
3. Does file end in `.md`?
4. Check `Failed/` folder for errors

### "Email not sending"

Check:
1. Gmail setup complete? (Step 3 above)
2. `config/credentials.json` exists?
3. `config/token.json` exists?
4. Email address correct?

### "WhatsApp not sending"

Check:
1. WhatsApp Web logged in?
2. Contact name spelled exactly as in WhatsApp?
3. Session exists in `whatsapp_session/` folder?

---

## Important Files to Keep

| File | Why It's Needed |
|------|-----------------|
| `Start_Auto_Processing.bat` | Main automation runner |
| `Execute_Approved.bat` | Manual processing |
| `Gmail_Auth.bat` | Gmail setup |
| `orchestrator.py` | The brain |
| `vault/` folder | Your work goes here |
| `config/credentials.json` | Gmail API access |
| `config/token.json` | Gmail login token |

---

## Tips

1. **Keep automation running** - Don't close the black window
2. **Use templates** - Copy from `vault/Templates/`
3. **Check Dashboard** - Open `vault/Dashboard.md` to see status
4. **Review Failed** - Check `Failed/` folder for errors
5. **Be patient** - Processing happens every 60 seconds

---

## Next Steps

1. ✅ Read this file completely
2. ✅ Set up Gmail (Step 3)
3. ✅ Start automation (Step 4)
4. ✅ Send test email (Step 5)
5. ✅ Read `GETTING_STARTED.md` for more details

---

## Need Help?

- Check `GETTING_STARTED.md` - More detailed guide
- Check `OBSIDIAN_WORKFLOW.md` - Obsidian-specific tips
- Check `Failed/` folder - Error messages
- Check `Dashboard.md` - System status

---

**You are ready to start!** 🎉

Run `Start_Auto_Processing.bat` now and follow the steps above.
