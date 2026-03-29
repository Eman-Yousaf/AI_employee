#!/usr/bin/env python3
"""Gmail IMAP Watcher - Simpler than API, just uses app password."""

import os
import email
import imaplib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class GmailIMAPWatcher:
    """Watch Gmail using IMAP (simpler than API)."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Get credentials from environment
        self.email = os.getenv('GMAIL_ADDRESS')
        self.password = os.getenv('GMAIL_APP_PASSWORD')

        if not self.email or not self.password:
            raise ValueError("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env file")

        self.keywords = ['urgent', 'invoice', 'payment', 'asap', 'meeting', 'quote']

    def connect(self):
        """Connect to Gmail IMAP."""
        try:
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(self.email, self.password)
            self.mail.select('inbox')
            logger.info(f"Connected to Gmail: {self.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def fetch_unread(self) -> List[Dict]:
        """Fetch unread emails."""
        try:
            _, messages = self.mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            emails = []
            for e_id in email_ids[-10:]:  # Last 10 unread
                _, msg_data = self.mail.fetch(e_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                subject = msg['subject'] or 'No Subject'
                from_addr = msg['from'] or 'Unknown'
                date = msg['date'] or datetime.now().isoformat()

                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore') if msg.get_payload() else ""

                emails.append({
                    'id': e_id.decode(),
                    'subject': subject,
                    'from': from_addr,
                    'date': date,
                    'body': body[:500],
                    'snippet': body[:200].replace('\n', ' ')
                })

            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def check_keywords(self, text: str) -> List[str]:
        """Check for priority keywords."""
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw in text_lower]

    def create_action_file(self, email_data: Dict) -> Path:
        """Create action file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_{timestamp}.md"
        filepath = self.needs_action / filename

        keywords_found = self.check_keywords(f"{email_data['subject']} {email_data['body']}")
        priority = 'high' if keywords_found else 'medium'

        content = f"""---
type: email
source: gmail
from: "{email_data['from']}"
subject: "{email_data['subject']}"
received: "{email_data['date']}"
priority: {priority}
keywords_found: {keywords_found}
status: pending
---

# Email: {email_data['subject']}

**From:** {email_data['from']}
**Date:** {email_data['date']}

## Preview
{email_data['snippet']}

## Keywords
{', '.join(keywords_found) if keywords_found else 'None'}

## Suggested Actions
- [ ] Review full email
- [ ] Draft response
- [ ] Mark complete
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created: {filename}")
        return filepath

    def run(self):
        """Run the watcher once."""
        if not self.connect():
            return

        emails = self.fetch_unread()
        logger.info(f"Found {len(emails)} unread emails")

        for email_data in emails:
            self.create_action_file(email_data)

        self.mail.close()
        self.mail.logout()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault-path', required=True)
    args = parser.parse_args()

    watcher = GmailIMAPWatcher(args.vault_path)
    watcher.run()


if __name__ == '__main__':
    main()
