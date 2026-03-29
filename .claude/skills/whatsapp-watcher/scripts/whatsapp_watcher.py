#!/usr/bin/env python3
"""WhatsApp Watcher - Monitors WhatsApp Web for unread messages."""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Playwright not installed")
    print("Run: pip install playwright && playwright install chromium")
    raise

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppWatcher:
    """Watcher for WhatsApp Web."""

    def __init__(self, vault_path: str, session_path: str, headless: bool = True):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)

        # Setup paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Session folder for persistent login
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Keywords for priority detection
        self.keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'pricing', 'quote', 'deadline', 'meeting', 'call',
            'problem', 'issue', 'question', 'interested', 'buy'
        ]

        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

        # Processed chats (to avoid duplicates)
        self.processed_file = self.vault_path / '.whatsapp_processed.json'
        self.processed_chats: Dict[str, str] = self._load_processed()

        logger.info(f"WhatsAppWatcher initialized")

    def _load_processed(self) -> Dict[str, str]:
        """Load previously processed chat timestamps."""
        if self.processed_file.exists():
            try:
                return json.loads(self.processed_file.read_text())
            except Exception as e:
                logger.error(f"Error loading processed: {e}")
        return {}

    def _save_processed(self):
        """Save processed chat timestamps."""
        try:
            self.processed_file.write_text(json.dumps(self.processed_chats, indent=2))
        except Exception as e:
            logger.error(f"Error saving processed: {e}")

    def start_browser(self) -> bool:
        """Start browser with persistent context."""
        try:
            playwright = sync_playwright().start()

            # Launch persistent context (maintains session)
            self.context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )

            self.page = self.context.new_page()

            # Navigate to WhatsApp Web
            logger.info("Navigating to WhatsApp Web...")
            try:
                # Try with domcontentloaded first (faster)
                self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
            except:
                # If that fails, just navigate without waiting
                self.page.goto('https://web.whatsapp.com')
                time.sleep(5)

            # Wait for QR scan or chat list
            try:
                # Check if already logged in
                self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=10000)
                logger.info("Already logged in to WhatsApp Web")
                return True
            except:
                # Need QR code scan
                logger.info("=" * 60)
                logger.info("SETUP REQUIRED: Scan QR Code")
                logger.info("=" * 60)
                logger.info("1. Open WhatsApp on your phone")
                logger.info("2. Go to Settings → Linked Devices → Link Device")
                logger.info("3. Scan the QR code in the browser")
                logger.info("=" * 60)
                logger.info("Waiting for QR scan (up to 2 minutes)...")

                self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
                logger.info("Successfully logged in")
                return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def get_unread_chats(self) -> List[Dict]:
        """Get list of chats with unread messages."""
        if not self.page:
            logger.error("Browser not started")
            return []

        try:
            # Refresh the page to get latest
            try:
                self.page.reload(wait_until='domcontentloaded', timeout=30000)
            except:
                self.page.reload()
                time.sleep(3)
            self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=30000)

            # Wait for chats to load
            time.sleep(3)

            # Find unread indicators
            unread_chats = []

            # Try different selectors for unread messages
            selectors = [
                'span[aria-label*="unread"]',
                'span[data-testid="icon-unread-count"]',
                'div[role="listitem"] span[class*="unread"]'
            ]

            for selector in selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    for elem in elements:
                        try:
                            # Get parent chat element
                            chat_elem = elem.evaluate('el => el.closest(\'[role="listitem"]\')')
                            if not chat_elem:
                                continue

                            # Extract chat info
                            title_elem = chat_elem.query_selector('[title]')
                            chat_name = title_elem.get_attribute('title') if title_elem else 'Unknown'

                            # Get message preview
                            preview_elem = chat_elem.query_selector('[class*="message"]')
                            preview = preview_elem.inner_text() if preview_elem else ''

                            # Get unread count
                            count_elem = chat_elem.query_selector('span[aria-label*="unread"]')
                            unread_count = count_elem.inner_text() if count_elem else '1'

                            chat_id = f"{chat_name}_{unread_count}"

                            # Check if already processed
                            if self.processed_chats.get(chat_id) == preview:
                                continue

                            unread_chats.append({
                                'name': chat_name,
                                'preview': preview,
                                'unread_count': unread_count,
                                'id': chat_id
                            })

                        except Exception as e:
                            logger.debug(f"Error processing chat element: {e}")
                            continue

                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            logger.info(f"Found {len(unread_chats)} unread chats")
            return unread_chats

        except Exception as e:
            logger.error(f"Error getting unread chats: {e}")
            return []

    def check_keywords(self, text: str) -> List[str]:
        """Check for priority keywords."""
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw in text_lower]

    def create_action_file(self, chat: Dict) -> Path:
        """Create action file for WhatsApp message."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = ''.join(c for c in chat['name'] if c.isalnum() or c in (' ', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')[:30]

        filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / filename

        # Determine priority
        keywords_found = self.check_keywords(f"{chat['name']} {chat['preview']}")
        priority = 'high' if keywords_found else 'medium'

        content = f"""---
type: whatsapp_message
source: whatsapp
chat_name: "{chat['name']}"
message_preview: "{chat['preview'][:200]}"
unread_count: {chat['unread_count']}
received: "{datetime.now().isoformat()}"
priority: {priority}
keywords_found: {keywords_found}
status: pending
---

# WhatsApp Message: {chat['name']}

**Chat:** {chat['name']}
**Unread Messages:** {chat['unread_count']}
**Priority:** {priority}

## Message Preview
```
{chat['preview'][:500]}
```

## Keywords Detected
{', '.join(keywords_found) if keywords_found else 'None'}

## Suggested Actions
- [ ] Open WhatsApp to read full message
- [ ] Check if invoice/payment related
- [ ] Reply if urgent
- [ ] Create task if needed

## Notes
_Open WhatsApp Web to see full conversation_
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created action file: {filepath.name}")

        # Mark as processed
        self.processed_chats[chat['id']] = chat['preview']

        return filepath

    def run_once(self) -> int:
        """Run one check cycle."""
        if not self.browser:
            if not self.start_browser():
                return 0

        chats = self.get_unread_chats()
        count = 0

        for chat in chats:
            try:
                self.create_action_file(chat)
                count += 1
            except Exception as e:
                logger.error(f"Error processing chat {chat['name']}: {e}")

        if count > 0:
            self._save_processed()
            logger.info(f"Created {count} action files")

        return count

    def run(self, interval: int = 60):
        """Run continuously."""
        logger.info(f"Starting WhatsApp Watcher (checking every {interval}s)")

        # Start browser
        if not self.start_browser():
            logger.error("Failed to start browser")
            return

        try:
            while True:
                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error in watch cycle: {e}")
                    # Try to restart browser on error
                    try:
                        self.context.close()
                    except:
                        pass
                    if not self.start_browser():
                        logger.error("Failed to restart browser")
                        break

                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Stopping WhatsApp Watcher...")
        finally:
            if self.context:
                self.context.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--session-path', default='./whatsapp_session', help='Path for session persistence')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--show-browser', action='store_true', help='Show browser window (not headless)')

    args = parser.parse_args()

    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        headless=not args.show_browser
    )

    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} chats")
        if watcher.context:
            watcher.context.close()
    else:
        watcher.run(interval=args.interval)


if __name__ == '__main__':
    main()
