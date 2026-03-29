# AI Employee - How To Use

## What You Now Have

A simple automation system with **only 5 files** in the main folder:

```
AI_employee/
│
├── START_HERE.md              ← Read this first
├── HOW_TO_USE.md              ← This file
├── orchestrator.py            ← The brain (don't touch)
│
├── Start_Auto_Processing.bat  ← RUN THIS (keeps running)
├── Execute_Approved.bat       ← Run manually if needed
├── Gmail_Auth.bat            ← Gmail setup (one time)
├── WhatsApp_Setup.bat        ← WhatsApp setup (one time)
│
├── scripts/
│   └── mcp_email_client.py   ← Email helper
│
├── .claude/skills/           ← Automation scripts (don't touch)
│
└── vault/                     ← YOUR OBSIDIAN VAULT
    ├── Pending_Approval/      ← Put draft emails here
    ├── Approved/              ← Drag files here to send
    ├── Done/                  ← Successfully sent items
    ├── Failed/                ← Errors
    └── Dashboard.md           ← See status here
```

---

## The Simple Workflow

### Step 1: Start Automation
Double-click: **Start_Auto_Processing.bat**
- Black window opens
- Press any key
- Leave it running (minimize it)
- ✅ This checks Approved/ folder every 60 seconds

### Step 2: Create Approval in Obsidian
1. Open Obsidian
2. Go to Pending_Approval/ folder
3. Create new note
4. Fill in the template
5. Save

### Step 3: Approve It
1. Drag the file to Approved/ folder
2. Automation detects it
3. Email/WhatsApp/LinkedIn sends automatically
4. File moves to Done/

---

## Templates (Copy These)

### Email Template

Create a file in Pending_Approval/ with this content:

```markdown
---
action: send_email
to: "recipient@example.com"
subject: "Subject line here"
priority: medium
---

Dear [Name],

[Your message here]

Best regards,
[Your name]
```

### WhatsApp Template

```markdown
---
action: send_whatsapp
chat_name: "Exact Contact Name"
priority: medium
---

[Your message here]
```

### LinkedIn Template

```markdown
---
action: social_post
platform: linkedin
---

[Your post content here]

#hashtag1 #hashtag2
```

---

## First-Time Setup

### 1. Set Up Gmail (Required for Email)

**You need credentials.json from Google Cloud Console.**

If you have it:
1. Put credentials.json in config/ folder
2. Double-click Gmail_Auth.bat
3. Follow login process
4. Done!

If you don't have credentials.json:
1. Go to https://console.cloud.google.com
2. Create new project
3. Search "Gmail API" and enable it
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Application type: Desktop app
6. Name it "AI Employee"
7. Download the JSON file
8. Rename to credentials.json
9. Put in config/ folder
10. Run Gmail_Auth.bat

### 2. Set Up WhatsApp (Required for WhatsApp)

1. Double-click WhatsApp_Setup.bat
2. Browser opens with WhatsApp Web
3. Scan QR code with your phone
4. Close browser when logged in
5. Done! Session is saved.

---

## Your Daily Workflow

### Morning:
1. Check Start_Auto_Processing.bat is running
2. Open Obsidian
3. Check Dashboard.md for status
4. Review Pending_Approval/

### Throughout Day:
1. Create new approvals in Pending_Approval/
2. Drag approved items to Approved/
3. System sends them automatically
4. Check Done/ for confirmation

### End of Day:
1. Check Failed/ for errors
2. Review Done/ for completed items
3. Check Logs/ if needed

---

## What Each Folder Does

| Folder | Purpose | What You Do |
|--------|---------|-------------|
| Pending_Approval/ | Draft emails/messages | Create, edit, review |
| Approved/ | Ready to send | Drag files here |
| Done/ | Successfully sent | Archive/check |
| Failed/ | Errors | Review/retry |
| Needs_Action/ | New items from Gmail | Review/create plans |
| Plans/ | Action plans | Reference |
| Templates/ | Copy-paste templates | Use as starting point |

---

## Common Tasks

### Send an Email:
1. Create file in Pending_Approval/
2. Use email template
3. Fill in to, subject, body
4. Save
5. Drag to Approved/
6. Check Done/ in 60 seconds

### Send WhatsApp:
1. Create file in Pending_Approval/
2. Use WhatsApp template
3. Fill in chat_name (exact name as in WhatsApp)
4. Fill in message
5. Drag to Approved/

### Post LinkedIn:
1. Create file in Pending_Approval/
2. Use LinkedIn template
3. Write post content
4. Add hashtags
5. Drag to Approved/

---

## Troubleshooting

### Nothing is sending
- Is Start_Auto_Processing.bat running?
- Are files in Approved/ folder?
- Do files end in .md?
- Check Failed/ folder

### Email not sending
- Gmail setup complete? (credentials.json + token.json)
- Is email address correct?
- Check Failed/ folder

### WhatsApp not sending
- WhatsApp setup complete?
- Is contact name exact?
- Check Failed/ folder

### Lost the black window
- Just run Start_Auto_Processing.bat again

---

## Batch Files Reference

| File | When To Use |
|------|-------------|
| Start_Auto_Processing.bat | **Run this and leave running** |
| Execute_Approved.bat | Run manually to process once |
| Gmail_Auth.bat | First-time Gmail setup only |
| WhatsApp_Setup.bat | First-time WhatsApp setup only |

---

## That's It!

You only need to:
1. Run Start_Auto_Processing.bat (once, leave it running)
2. Use Obsidian to create and approve items
3. Everything else is automatic!

**Read START_HERE.md for more details.**
