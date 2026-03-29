---
name: gmail-watcher
description: |
  Monitor Gmail inbox for new unread/important emails and create action files in the Obsidian vault.
  Watches for urgent emails and converts them to markdown files in /Needs_Action for Claude to process.
  Use for email triage, lead capture, and urgent message detection.
---

# Gmail Watcher

Monitors Gmail for unread important messages and creates action files in the Obsidian vault.

## Prerequisites

1. Gmail API credentials (credentials.json) from Google Cloud Console
2. Python 3.13+ with google-api-python-client installed
3. Vault path configured

## Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API: APIs & Services > Library > Search "Gmail API" > Enable
4. Create OAuth credentials: APIs & Services > Credentials > Create Credentials > OAuth client ID
5. Download credentials.json

### 2. Authentication

```bash
# Run auth flow once to get token.json
python scripts/gmail_auth.py
```

## Usage

### Start Watcher

```bash
# Using PM2 (recommended for continuous monitoring)
pm2 start scripts/gmail_watcher.py --interpreter python3 -- --vault-path /path/to/vault

# Or run directly
python scripts/gmail_watcher.py --vault-path /path/to/vault
```

### Configuration

Create `config/gmail_watcher.json`:

```json
{
  "vault_path": "/path/to/AI_Employee_Vault",
  "credentials_path": "config/credentials.json",
  "check_interval": 120,
  "query": "is:unread is:important",
  "keywords": ["urgent", "invoice", "payment", "asap", "deadline"]
}
```

## Output Format

Created files in `/Needs_Action/`:

```markdown
---
type: email
source: gmail
message_id: 12345abc
from: client@example.com
subject: "Urgent: Invoice Payment"
received: 2026-01-07T10:30:00Z
priority: high
keywords_found: ["urgent", "invoice"]
status: pending
---

## Email Content
Snippet of email content...

## Suggested Actions
- [ ] Reply to sender
- [ ] Create invoice task
- [ ] Forward to accounting
```

## File Naming Convention

- Format: `EMAIL_{sender}_{timestamp}.md`
- Example: `EMAIL_client.example_2026-01-07T103000.md`

## Integration

The watcher integrates with the orchestrator:

1. Watcher detects new email
2. Creates action file in `/Needs_Action/`
3. Orchestrator notifies Claude Code
4. Claude processes according to Company_Handbook.md rules

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Verify OAuth consent screen is configured |
| Token expired | Re-run `python scripts/gmail_auth.py` |
| No emails found | Check query string, try `is:unread` only |
| Vault not found | Verify absolute path in config |

## Security

- Never commit `credentials.json` or `token.json`
- Add to `.gitignore`:
  ```
  config/credentials.json
  config/token.json
  ```
- Use read-only Gmail scope when possible
- Rotate credentials monthly

## Verification

```bash
python scripts/verify_gmail.py
```

Expected: `✓ Gmail API connected, X unread messages found`
