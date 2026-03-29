#!/usr/bin/env python3
"""WhatsApp Sender - Send messages via WhatsApp Web using Playwright."""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Playwright not installed")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Send WhatsApp messages via WhatsApp Web."""

    def __init__(self, session_path: str, headless: bool = False):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless

        self.browser = None
        self.context = None
        self.page = None

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
                self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
            except:
                self.page.goto('https://web.whatsapp.com')
                time.sleep(5)

            # Wait for QR scan or chat list
            try:
                # Check if already logged in
                self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=15000)
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

                try:
                    self.page.wait_for_selector('[data-testid="chat-list-search"]', timeout=120000)
                    logger.info("Successfully logged in")
                    return True
                except Exception as e:
                    logger.error(f"Login timeout: {e}")
                    return False

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def find_chat(self, chat_name: str) -> bool:
        """Find and open a chat by name."""
        try:
            logger.info(f"Searching for chat: {chat_name}")

            # Click on search box
            search_box = self.page.locator('[data-testid="chat-list-search"]').first
            search_box.click()
            time.sleep(0.5)

            # Clear existing text
            search_box.fill("")
            time.sleep(0.3)

            # Type search query
            search_box.fill(chat_name)
            time.sleep(2)  # Wait for results

            # Try to find and click the chat
            # First try exact title match
            chat_selector = f'[title="{chat_name}"]'
            try:
                chat_elem = self.page.locator(chat_selector).first
                chat_elem.click(timeout=5000)
                logger.info(f"Found chat: {chat_name}")
                time.sleep(1)
                return True
            except:
                pass

            # Try partial match
            try:
                chat_elem = self.page.locator('span[title*="{}"]'.format(chat_name[:10])).first
                chat_elem.click(timeout=5000)
                logger.info(f"Found chat (partial match): {chat_name}")
                time.sleep(1)
                return True
            except:
                pass

            # Try clicking first result
            try:
                results = self.page.locator('[data-testid="cell-frame-container"]').all()
                if results:
                    results[0].click()
                    logger.info(f"Clicked first search result for: {chat_name}")
                    time.sleep(1)
                    return True
            except:
                pass

            logger.error(f"Could not find chat: {chat_name}")
            return False

        except Exception as e:
            logger.error(f"Error finding chat: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """Send a message in the currently open chat."""
        try:
            logger.info("Sending message...")

            # Find message input box
            # Try different selectors
            selectors = [
                '[data-testid="conversation-compose-box-input"]',
                '[data-testid="compose-box-input"]',
                'div[contenteditable="true"]',
                'div[role="textbox"]'
            ]

            input_box = None
            for selector in selectors:
                try:
                    input_box = self.page.locator(selector).first
                    if input_box.is_visible(timeout=2000):
                        break
                except:
                    continue

            if not input_box:
                logger.error("Could not find message input box")
                return False

            # Click and type message
            input_box.click()
            time.sleep(0.5)

            # Type message
            input_box.fill(message)
            time.sleep(0.5)

            # Press Enter to send
            self.page.keyboard.press('Enter')
            time.sleep(1)

            logger.info("Message sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_to_chat(self, chat_name: str, message: str) -> bool:
        """Send message to a specific chat."""
        if not self.context:
            if not self.start_browser():
                return False

        # Find the chat
        if not self.find_chat(chat_name):
            return False

        # Send the message
        return self.send_message(message)

    def close(self):
        """Close browser."""
        if self.context:
            self.context.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='WhatsApp Sender')
    parser.add_argument('--chat', required=True, help='Chat name to send message to')
    parser.add_argument('--message', required=True, help='Message to send')
    parser.add_argument('--session-path', default='./whatsapp_session', help='Session path')
    parser.add_argument('--headless', action='store_true', help='Run headless')

    args = parser.parse_args()

    sender = WhatsAppSender(session_path=args.session_path, headless=args.headless)

    try:
        success = sender.send_to_chat(args.chat, args.message)
        if success:
            print(f"✅ Message sent to {args.chat}")
        else:
            print(f"❌ Failed to send message")
            sys.exit(1)
    finally:
        sender.close()


if __name__ == '__main__':
    main()
