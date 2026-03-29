#!/usr/bin/env python3
"""Email MCP Server - MCP server for Gmail operations."""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from base64 import urlsafe_b64encode
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    print("Google API not installed. Run: pip install google-api-python-client")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailMCP:
    """Email MCP Server implementing Model Context Protocol."""

    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = Path(credentials_path or os.getenv('GMAIL_CREDENTIALS', 'config/credentials.json'))
        self.token_path = Path(token_path or os.getenv('GMAIL_TOKEN', 'config/token.json'))

        self.service = None
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.auth_error = None

        try:
            self._authenticate()
        except Exception as e:
            logger.error(f"Email MCP initialization failed: {e}")
            self.auth_error = str(e)

    def _authenticate(self):
        """Authenticate with Gmail API with better error handling."""
        errors = []

        try:
            creds = None

            # Check if token exists
            if self.token_path.exists():
                try:
                    logger.info(f"Loading token from {self.token_path}")
                    creds = Credentials.from_authorized_user_file(str(self.token_path))
                    logger.info("Token loaded successfully")
                except Exception as e:
                    errors.append(f"Token load failed: {e}")
                    creds = None

            # Check token validity
            if creds:
                if creds.valid:
                    logger.info("Token is valid")
                elif creds.expired and creds.refresh_token:
                    try:
                        logger.info("Token expired, refreshing...")
                        creds.refresh(Request())
                        self.token_path.write_text(creds.to_json())
                        logger.info("Token refreshed")
                    except Exception as e:
                        errors.append(f"Token refresh failed: {e}")
                        creds = None
                else:
                    errors.append("Token invalid and no refresh token")
                    creds = None

            if not creds:
                error_msg = """Authentication failed. Please run Gmail authentication first.

Steps:
1. Run: python .claude/skills/gmail-watcher/scripts/gmail_auth.py
   Or double-click: Gmail_Auth.bat

2. If that fails, try manual auth:
   python scripts/gauth_helper.py

3. Make sure you have:
   - config/credentials.json (from Google Cloud Console)
   - Enabled Gmail API in Google Cloud Console
   - Configured OAuth consent screen

Errors encountered:
""" + "\n".join(errors)
                logger.error(error_msg)
                raise Exception(error_msg)

            # Build service
            self.service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
            logger.info("Email MCP authenticated successfully")

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            # Don't raise here - let the caller handle it
            self.auth_error = str(e)

    def list_tools(self) -> List[Dict]:
        """List available MCP tools."""
        return [
            {
                "name": "email_send",
                "description": "Send an email immediately",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body (text or HTML)"},
                        "cc": {"type": "array", "items": {"type": "string"}},
                        "bcc": {"type": "array", "items": {"type": "string"}},
                        "is_html": {"type": "boolean", "default": False}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "email_draft",
                "description": "Create a draft email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "is_html": {"type": "boolean", "default": False}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "email_read",
                "description": "Read an email by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string"},
                        "format": {"type": "string", "enum": ["minimal", "full"], "default": "full"}
                    },
                    "required": ["message_id"]
                }
            },
            {
                "name": "email_search",
                "description": "Search emails with Gmail query syntax",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Gmail search query"},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            }
        ]

    def send_email(self, params: Dict) -> Dict:
        """Send an email."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would send email to {params.get('to')}")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would send to {params.get('to')}"
            }

        try:
            to = params.get('to')
            subject = params.get('subject')
            body = params.get('body')
            is_html = params.get('is_html', False)
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['To'] = to

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Add body
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type))

            # Encode and send
            raw_message = urlsafe_b64encode(msg.as_bytes()).decode()
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent successfully: {result.get('id')}")

            return {
                "success": True,
                "message_id": result.get('id'),
                "thread_id": result.get('threadId'),
                "to": to,
                "subject": subject
            }

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_draft(self, params: Dict) -> Dict:
        """Create a draft email."""
        try:
            to = params.get('to')
            subject = params.get('subject')
            body = params.get('body')
            is_html = params.get('is_html', False)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['To'] = to

            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type))

            raw_message = urlsafe_b64encode(msg.as_bytes()).decode()

            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()

            logger.info(f"Draft created: {draft.get('id')}")

            return {
                "success": True,
                "draft_id": draft.get('id'),
                "message_id": draft.get('message', {}).get('id')
            }

        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def read_email(self, params: Dict) -> Dict:
        """Read an email by ID."""
        try:
            message_id = params.get('message_id')
            format_type = params.get('format', 'full')

            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format_type
            ).execute()

            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}

            # Extract body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                data = message['payload'].get('body', {}).get('data', '')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8')

            return {
                "success": True,
                "message_id": message_id,
                "thread_id": message.get('threadId'),
                "headers": headers,
                "body": body[:1000],  # Limit body size
                "snippet": message.get('snippet'),
                "labels": message.get('labelIds', [])
            }

        except Exception as e:
            logger.error(f"Failed to read email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_emails(self, params: Dict) -> Dict:
        """Search emails."""
        try:
            query = params.get('query')
            max_results = params.get('max_results', 10)

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            return {
                "success": True,
                "count": len(messages),
                "messages": [
                    {
                        "id": m['id'],
                        "thread_id": m.get('threadId')
                    }
                    for m in messages
                ]
            }

        except Exception as e:
            logger.error(f"Failed to search emails: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def handle_request(self, request: Dict) -> Dict:
        """Handle an MCP request."""
        tool = request.get('tool')
        params = request.get('params', {})

        handlers = {
            'email_send': self.send_email,
            'email_draft': self.create_draft,
            'email_read': self.read_email,
            'email_search': self.search_emails,
            'tools/list': lambda _: {"tools": self.list_tools()}
        }

        handler = handlers.get(tool)
        if handler:
            return handler(params)
        else:
            return {"error": f"Unknown tool: {tool}"}


def run_stdio():
    """Run MCP server in stdio mode (for Claude Code integration)."""
    mcp = EmailMCP()

    logger.info("Email MCP Server started (stdio mode)")

    while True:
        try:
            line = input()
            if not line:
                continue

            request = json.loads(line)
            response = mcp.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()

        except EOFError:
            break
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            print(json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            print(json.dumps({"error": str(e)}))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--token', help='Path to token.json')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')

    args = parser.parse_args()

    if args.dry_run:
        os.environ['DRY_RUN'] = 'true'

    try:
        run_stdio()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == '__main__':
    main()
