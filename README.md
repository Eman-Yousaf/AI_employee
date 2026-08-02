# AI Employee

An automated AI employee that handles your business communications: emails, WhatsApp messages, and LinkedIn posts - all controlled from Obsidian.

## Features

- **📧 Email Automation** - Send emails via Gmail with approval workflow
- **💬 WhatsApp Automation** - Send WhatsApp messages automatically
- **💼 LinkedIn Automation** - Generate and post LinkedIn content
- **✅ Human-in-the-Loop** - All actions require your approval
- **📝 Obsidian Integration** - Control everything from your Obsidian vault
- **🤖 Auto-Processing** - Run continuously in the background

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Services

#### Gmail (for email sending)
1. Get credentials.json from Google Cloud Console
2. Put in `config/` folder
3. Run `Gmail_Auth.bat`

#### WhatsApp
1. Run `WhatsApp_Setup.bat`
2. Scan QR code with your phone

#### LinkedIn
1. Run `Test_LinkedIn_Only.bat`
2. Login in browser

### 3. Start Automation

Double-click: `Start_Auto_Processing.bat`

Leave this running - it processes approvals automatically.

### 4. Use in Obsidian

1. Open the `vault` folder in Obsidian
2. Create files in `Pending_Approval/`
3. Drag to `Approved/` to execute
4. Check `Done/` for confirmation

## How It Works

```
Pending_Approval/ → Approved/ → [System Executes] → Done/
```

1. **Create** a file with email/message details
2. **Review** and approve (drag to Approved/)
3. **System sends** automatically
4. **File moves** to Done/

## File Structure

```
AI_employee/
│
├── Start_Auto_Processing.bat  # Main automation runner
├── orchestrator.py            # Core automation script
│
├── vault/                     # Your Obsidian vault
│   ├── Pending_Approval/      # Draft items
│   ├── Approved/              # Ready to execute
│   ├── Done/                  # Completed items
│   └── Templates/             # Copy-paste templates
│
├── .claude/skills/            # Automation modules
│   ├── approval-workflow/     # Execute approved actions
│   ├── email-mcp/            # Email MCP server
│   ├── gmail-watcher/        # Gmail monitoring
│   ├── linkedin-poster/      # LinkedIn automation
│   ├── plan-creator/         # Plan generation
│   └── whatsapp-watcher/     # WhatsApp automation
│
└── config/                    # Your credentials (not shared)
    ├── credentials.json       # Get from Google Cloud
    └── token.json            # Auto-generated
```

## Templates

### Email Template
```markdown
---
action: send_email
to: "recipient@example.com"
subject: "Subject"
priority: medium
---

Your email body here.
```

### WhatsApp Template
```markdown
---
action: send_whatsapp
chat_name: "Contact Name"
priority: medium
---

Your message here.
```

### LinkedIn Template
```markdown
---
action: social_post
platform: linkedin
---

Your post content here.

#hashtag1 #hashtag2
```

## Available Batch Files

| File | Purpose |
|------|---------|
| `Start_Auto_Processing.bat` | Run automation continuously |
| `Execute_Approved.bat` | Process approved items once |
| `Gmail_Auth.bat` | Gmail setup |
| `WhatsApp_Setup.bat` | WhatsApp setup |
| `Test_All_Setup.bat` | Test all configurations |
| `Send_All_Now.bat` | Send test messages |
| `CHECK_BEFORE_GITHUB.bat` | Verify privacy before sharing |

## Security & Privacy

- **Human approval required** - Nothing sends without your approval
- **Audit trail** - All actions logged in `Done/` folder
- **Local processing** - Your data stays on your computer
- **Credential protection** - See GITHUB_GUIDE.md for safe sharing

## Requirements

- Windows 10/11
- Python 3.10+
- Obsidian (optional but recommended)
- Gmail account
- WhatsApp on phone
- LinkedIn account

## Setup Guides

- **First Time Setup:** See `START_HERE.md`
- **Detailed Guide:** See `HOW_TO_USE.md`
- **GitHub Sharing:** See `GITHUB_GUIDE.md`
- **Testing:** See `TESTING_GUIDE.md`

## Troubleshooting

### "Nothing sending"
- Is `Start_Auto_Processing.bat` running?
- Are files in `Approved/` folder?

### "Email not working"
- Run `Test_Email_Only.bat`
- Check `config/credentials.json` exists

### "WhatsApp not working"
- Run `Test_WhatsApp_Only.bat`
- Check if logged in to WhatsApp Web

### "LinkedIn not working"
- Run `Test_LinkedIn_Only.bat`
- Check if logged in to LinkedIn

## License

MIT - Feel free to use and modify!

## Credits

Built with:
- Python
- Playwright
- Gmail API
- Obsidian
