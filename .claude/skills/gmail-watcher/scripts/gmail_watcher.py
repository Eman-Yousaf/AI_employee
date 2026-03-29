#!/usr/bin/env python3
"""Gmail Watcher - Monitors Gmail inbox and creates action files."""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Set, Optional

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("Google API not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    raise

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message."""
    id: str
    thread_id: str
    from_addr: str
    to_addr: str
    subject: str
    date: str
    snippet: str
    labels: List[str]


class GmailWatcher:
    """Watcher for Gmail inbox."""

    def __init__(self, vault_path: str, credentials_path: str, token_path: str = None):
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else self.credentials_path.parent / 'token.json'

        # Setup paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Processed message IDs (persisted to file)
        self.processed_ids_file = self.vault_path / '.processed_ids.json'
        self.processed_ids: Set[str] = self._load_processed_ids()

        # Keywords for priority detection
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'deadline', 'meeting']

        # Gmail service
        self.service = None

        logger.info(f"GmailWatcher initialized with vault: {self.vault_path}")

    def _load_processed_ids(self) -> Set[str]:
        """Load previously processed message IDs."""
        if self.processed_ids_file.exists():
            try:
                data = json.loads(self.processed_ids_file.read_text())
                return set(data.get('processed_ids', []))
            except Exception as e:
                logger.error(f"Error loading processed IDs: {e}")
        return set()

    def _save_processed_ids(self):
        """Save processed message IDs."""
        try:
            data = {'processed_ids': list(self.processed_ids), 'last_updated': datetime.now().isoformat()}
            self.processed_ids_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving processed IDs: {e}")

    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            creds = None

            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(str(self.token_path))

            # Refresh or create credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing credentials...")
                    creds.refresh(Request())
                else:
                    logger.error("No valid credentials. Run gmail_auth.py first.")
                    return False

                # Save refreshed token
                self.token_path.write_text(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Successfully authenticated with Gmail")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def fetch_unread_messages(self, max_results: int = 10) -> List[EmailMessage]:
        """Fetch unread important messages from Gmail."""
        if not self.service:
            logger.error("Not authenticated")
            return []

        try:
            # Search for unread and important messages
            query = 'is:unread is:important'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread important messages")

            email_messages = []
            for msg in messages:
                if msg['id'] in self.processed_ids:
                    continue

                # Fetch full message details
                detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in detail['payload'].get('headers', [])}

                email_msg = EmailMessage(
                    id=msg['id'],
                    thread_id=msg['threadId'],
                    from_addr=headers.get('From', 'Unknown'),
                    to_addr=headers.get('To', 'Unknown'),
                    subject=headers.get('Subject', 'No Subject'),
                    date=headers.get('Date', datetime.now().isoformat()),
                    snippet=detail.get('snippet', ''),
                    labels=detail.get('labelIds', [])
                )
                email_messages.append(email_msg)

            return email_messages

        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []

    def check_keywords(self, email: EmailMessage) -> List[str]:
        """Check for priority keywords in email."""
        text = f"{email.subject} {email.snippet}".lower()
        found = [kw for kw in self.keywords if kw in text]
        return found

    def create_action_file(self, email: EmailMessage) -> Path:
        """Create an action file for the email."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_{email.id[:8]}_{timestamp}.md"
        filepath = self.needs_action / filename

        # Determine priority
        keywords_found = self.check_keywords(email)
        priority = 'high' if keywords_found else 'medium'

        # Extract sender name/email
        from_field = email.from_addr
        if '<' in from_field:
            sender_name = from_field.split('<')[0].strip()
            sender_email = from_field.split('<')[1].rstrip('>')
        else:
            sender_name = from_field
            sender_email = from_field

        content = f"""---
type: email
source: gmail
message_id: {email.id}
thread_id: {email.thread_id}
from_name: "{sender_name}"
from_email: "{sender_email}"
to: "{email.to_addr}"
subject: "{email.subject}"
received: "{email.date}"
priority: {priority}
keywords_found: {keywords_found}
status: pending
---

# Email: {email.subject}

**From:** {email.from_addr}
**Date:** {email.date}
**Priority:** {priority}

## Content Preview
```
{email.snippet[:500]}
```

## Keywords Detected
{', '.join(keywords_found) if keywords_found else 'None'}

## Suggested Actions
- [ ] Review email content
- [ ] Draft response if needed
- [ ] Update Dashboard if urgent

## Notes
_Add any notes here as you process this email_
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created action file: {filepath.name}")
        return filepath

    def run_once(self) -> int:
        """Run one check cycle. Returns number of new messages processed."""
        if not self.service and not self.authenticate():
            return 0

        messages = self.fetch_unread_messages()
        count = 0

        for msg in messages:
            try:
                self.create_action_file(msg)
                self.processed_ids.add(msg.id)
                count += 1
            except Exception as e:
                logger.error(f"Error processing message {msg.id}: {e}")

        if count > 0:
            self._save_processed_ids()
            logger.info(f"Processed {count} new messages")

        return count

    def run(self, interval: int = 120):
        """Run continuously with specified interval (seconds)."""
        logger.info(f"Starting Gmail Watcher (checking every {interval}s)")

        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in watch cycle: {e}")

            logger.debug(f"Sleeping for {interval}s...")
            time.sleep(interval)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--credentials', default='config/credentials.json', help='Path to credentials.json')
    parser.add_argument('--token', default='config/token.json', help='Path to token.json')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials,
        token_path=args.token
    )

    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} messages")
    else:
        watcher.run(interval=args.interval)


if __name__ == '__main__':
    main()
