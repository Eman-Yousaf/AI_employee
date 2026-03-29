---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for unread messages containing specific keywords.
  Uses Playwright to watch for urgent messages and creates action files in the vault.
  Use for lead capture, urgent client communication, and payment reminders.
  Note: Requires WhatsApp Web session (scanned QR code persists in session folder).
---

# WhatsApp Watcher

Monitors WhatsApp Web for unread messages with keywords and creates action files.

## Prerequisites

1. Playwright installed: `pip install playwright && playwright install chromium`
2. WhatsApp Web session folder (for persistent login)
3. Sufficient disk space for browser profile (~50MB)

## Setup

### 1. Initial QR Code Scan

```bash
# Run interactive setup to scan QR code
python scripts/whatsapp_setup.py --session-path ./whatsapp_session
```

Scan the displayed QR code with your phone (WhatsApp > Linked Devices).

### 2. Verify Session

```bash
python scripts/verify_whatsapp.py --session-path ./whatsapp_session
```

Expected: `✓ WhatsApp Web session active`

## Usage

### Start Watcher

```bash
# Using PM2
pm2 start scripts/whatsapp_watcher.py --interpreter python3 -- --vault-path /path/to/vault --session-path ./whatsapp_session

# Or run directly
python scripts/whatsapp_watcher.py --vault-path /path/to/vault --session-path ./whatsapp_session
```

### Configuration

Create `config/whatsapp_watcher.json`:

```json
{
  "vault_path": "/path/to/AI_Employee_Vault",
  "session_path": "./whatsapp_session",
  "check_interval": 30,
  "keywords": ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote", "deadline"],
  "ignore_groups": true,
  "ignore_contacts": ["Family Group", "Friends Chat"]
}
```

## Output Format

Created files in `/Needs_Action/`:

```markdown
---
type: whatsapp_message
source: whatsapp
chat_name: "Client A"
message_preview: "Hey, can you send me the invoice for January?"
received: 2026-01-07T10:30:00Z
keywords_found: ["invoice"]
priority: high
status: pending
---

## Message Context
From: Client A
Time: 10:30 AM
Keywords detected: invoice

## Suggested Actions
- [ ] Generate invoice for January
- [ ] Reply with payment link
- [ ] Log to accounting
```

## File Naming Convention

- Format: `WHATSAPP_{chat_name}_{timestamp}.md`
- Example: `WHATSAPP_Client_A_2026-01-07T103000.md`

## How It Works

1. Playwright launches headless Chromium with persistent context
2. Navigates to web.whatsapp.com (already logged in from session)
3. Scans chat list for unread message indicators
4. Checks message text against keywords
5. Creates action file for matching messages

## Security & Privacy

- Session data contains your WhatsApp login - protect it!
- Never commit `whatsapp_session/` folder
- Add to `.gitignore`:
  ```
  whatsapp_session/
  ```
- Run in headless mode (no visible browser)
- WhatsApp Web session expires after ~14 days of inactivity

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code keeps showing | Delete session folder and re-scan |
| Session expired | Re-run setup script |
| Messages not detected | Increase check_interval, check keywords |
| Browser won't start | Verify Playwright installed: `playwright install chromium` |
| WhatsApp blocks automation | Reduce check_interval to 60+ seconds |

## Limitations

- Requires persistent server/desktop (not serverless)
- WhatsApp may rate-limit or block automation
- Session expires after period of inactivity
- Only works with WhatsApp Web, not Business API

## Verification

```bash
python scripts/verify_whatsapp.py --session-path ./whatsapp_session
```

Expected: `✓ Session valid, X unread chats found`
