---
name: email-mcp
description: |
  MCP (Model Context Protocol) server for email operations.
  Provides send, draft, read, and search capabilities for Gmail.
  Enables Claude to send emails, create drafts, and manage inbox.
  Use for automated email responses, notifications, and outreach.
---

# Email MCP Server

MCP server providing email capabilities to Claude Code.

## Overview

The Email MCP server exposes email operations as tools that Claude can invoke:

- `email_send` - Send an email immediately
- `email_draft` - Create a draft email
- `email_read` - Read email content by ID
- `email_search` - Search inbox
- `email_list` - List recent emails

## Installation

### Option 1: Use Existing MCP Server

```bash
# Install email MCP from community
npm install -g @anthropic/email-mcp
# or
pip install email-mcp-server
```

### Option 2: Custom Implementation

Create `servers/email_mcp.py`:

```python
#!/usr/bin/env python3
"""Email MCP Server for Gmail integration."""

import asyncio
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# MCP protocol implementation
class EmailMCPServer:
    def __init__(self):
        self.creds = Credentials.from_authorized_user_file(
            os.getenv('GMAIL_CREDENTIALS', 'config/token.json')
        )
        self.service = build('gmail', 'v1', credentials=self.creds)

    async def handle_request(self, request):
        tool = request.get('tool')
        params = request.get('params', {})

        if tool == 'email_send':
            return await self.send_email(params)
        elif tool == 'email_draft':
            return await self.create_draft(params)
        elif tool == 'email_read':
            return await self.read_email(params)
        elif tool == 'email_search':
            return await self.search_emails(params)
        else:
            return {'error': f'Unknown tool: {tool}'}

    async def send_email(self, params):
        # Implementation
        pass

    async def create_draft(self, params):
        # Implementation
        pass

    async def read_email(self, params):
        # Implementation
        pass

    async def search_emails(self, params):
        # Implementation
        pass

if __name__ == '__main__':
    server = EmailMCPServer()
    # Start MCP server (stdio or sse)
```

## Claude Code Configuration

Add to Claude Code settings (`~/.config/claude-code/settings.json`):

```json
{
  "mcpServers": [
    {
      "name": "email",
      "command": "python",
      "args": ["/path/to/servers/email_mcp.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/config/token.json"
      }
    }
  ]
}
```

Or use the newer format:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["servers/email_mcp.py"],
      "env": {
        "GMAIL_CREDENTIALS": "config/token.json"
      }
    }
  }
}
```

## Available Tools

### email_send

Send an email immediately.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello from AI Employee",
  "body": "Email body text (can include HTML)",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "attachments": ["/path/to/file.pdf"],
  "is_html": false
}
```

**Returns:**
```json
{
  "success": true,
  "message_id": "12345abc",
  "thread_id": "thread_123"
}
```

### email_draft

Create a draft email (saved but not sent).

**Parameters:** Same as `email_send`

**Returns:**
```json
{
  "success": true,
  "draft_id": "draft_123",
  "preview_url": "https://mail.google.com/..."
}
```

### email_read

Read a specific email by ID.

**Parameters:**
```json
{
  "message_id": "12345abc",
  "format": "full"
}
```

**Returns:**
```json
{
  "message_id": "12345abc",
  "thread_id": "thread_123",
  "headers": {
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Subject",
    "date": "2026-01-07T10:30:00Z"
  },
  "body": "Email body text",
  "attachments": []
}
```

### email_search

Search emails with Gmail query syntax.

**Parameters:**
```json
{
  "query": "is:unread from:client@example.com",
  "max_results": 10
}
```

**Returns:**
```json
{
  "messages": [
    {
      "id": "12345abc",
      "thread_id": "thread_123",
      "snippet": "Preview text..."
    }
  ],
  "result_size_estimate": 5
}
```

## Safety Controls

### Dry Run Mode

Set `DRY_RUN=true` to log actions without sending:

```bash
DRY_RUN=true python servers/email_mcp.py
```

### Rate Limiting

Configure max emails per hour:

```json
{
  "rate_limits": {
    "emails_per_hour": 20,
    "emails_per_day": 100
  }
}
```

### Approval Required

Configure which emails require approval:

```json
{
  "approval_rules": {
    "new_recipients": true,
    "bulk_sends": true,
    "attachments": true,
    "external_domains": ["gmail.com", "yahoo.com"]
  }
}
```

## Human-in-the-Loop Integration

Instead of direct sending, the MCP can create approval files:

```python
# In email_mcp.py
def send_email(self, params):
    if self.requires_approval(params):
        # Create approval file instead of sending
        approval_file = self.create_approval_request(params)
        return {
            "success": false,
            "requires_approval": true,
            "approval_file": approval_file
        }
    # Otherwise send directly
    return self._do_send(params)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP not connecting | Verify server path in settings.json |
| Authentication failed | Check GMAIL_CREDENTIALS path, re-auth if needed |
| Rate limit exceeded | Reduce volume, implement exponential backoff |
| Tool not found | Restart Claude Code after config changes |

## Verification

```bash
# Test MCP server
python scripts/mcp_client.py --server email --tool email_search --params '{"query": "is:unread", "max_results": 5}'
```

Expected: `✓ MCP connected, found X unread emails`

## Security

- Run MCP server with minimal privileges
- Use dedicated Gmail account (not personal)
- Enable Gmail audit logging
- Review sent emails in Gmail Sent folder
- Never log email content with sensitive data
