#!/usr/bin/env python3
"""Monitor Approved folder and execute approved actions."""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApprovalMonitor:
    """Monitors /Approved folder and executes actions."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.failed = self.vault_path / 'Failed'

        self.approved.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        self.failed.mkdir(parents=True, exist_ok=True)

        # Get credentials paths
        self.credentials_path = Path(__file__).parent.parent.parent.parent / 'config' / 'credentials.json'
        self.token_path = Path(__file__).parent.parent.parent.parent / 'config' / 'token.json'

        logger.info(f"ApprovalMonitor initialized")
        logger.info(f"Vault: {self.vault_path}")

    def parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter."""
        if not content.startswith('---'):
            return {}

        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}

            frontmatter = parts[1].strip()
            metadata = {}

            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    metadata[key] = value

            return metadata

        except Exception as e:
            logger.error(f"Error parsing frontmatter: {e}")
            return {}

    def extract_body_from_markdown(self, content: str) -> str:
        """Extract email body from markdown content."""
        # Split on --- to remove frontmatter
        parts = content.split('---')
        if len(parts) >= 3:
            body_content = parts[2]
        else:
            body_content = content

        # Remove markdown headers and get clean text
        lines = body_content.split('\n')
        body_lines = []
        for line in lines:
            # Skip empty lines at start
            if not body_lines and not line.strip():
                continue
            body_lines.append(line)

        return '\n'.join(body_lines).strip()

    def execute_email(self, metadata: Dict, content: str) -> bool:
        """Execute approved email send using Email MCP."""
        try:
            to = metadata.get('to')
            subject = metadata.get('subject')
            body = metadata.get('body')

            if not to or not subject:
                logger.error("Missing required email fields (to, subject)")
                return False

            # If body not in metadata, extract from content
            if not body:
                body = self.extract_body_from_markdown(content)

            # If still no body, use a default
            if not body:
                body = "(No message body)"

            logger.info(f"Sending email to {to}: {subject}")

            # Call MCP Email Client
            mcp_client = Path(__file__).parent.parent.parent.parent.parent / 'scripts' / 'mcp_email_client.py'

            if not mcp_client.exists():
                logger.error(f"MCP client not found: {mcp_client}")
                return False

            params = {
                "to": to,
                "subject": subject,
                "body": body,
                "is_html": metadata.get('is_html', 'false').lower() == 'true'
            }

            result = subprocess.run(
                [sys.executable, str(mcp_client),
                 '--tool', 'email_send',
                 '--params', json.dumps(params),
                 '--credentials', str(self.credentials_path),
                 '--token', str(self.token_path)],
                capture_output=True, text=True, timeout=60
            )

            logger.debug(f"MCP result: {result.stdout}")
            logger.debug(f"MCP stderr: {result.stderr}")

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        logger.info(f"✅ Email sent successfully: {response.get('message_id')}")
                        return True
                    else:
                        logger.error(f"❌ Email send failed: {response.get('error')}")
                        return False
                except json.JSONDecodeError:
                    if 'message_id' in result.stdout:
                        logger.info(f"✅ Email sent (parsed from output)")
                        return True
                    logger.error(f"❌ Could not parse MCP response: {result.stdout}")
                    return False
            else:
                logger.error(f"❌ MCP client failed with code {result.returncode}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Email send timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False

    def execute_whatsapp(self, metadata: Dict, content: str) -> bool:
        """Execute approved WhatsApp message."""
        try:
            chat_name = metadata.get('chat_name') or metadata.get('to')
            message = metadata.get('message')

            if not chat_name:
                logger.error("Missing chat_name for WhatsApp message")
                return False

            if not message:
                # Try to extract from content
                lines = content.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#') and not line.startswith('---'):
                        message = line.strip()
                        break

            if not message:
                message = metadata.get('body', '(No message)')

            logger.info(f"Sending WhatsApp message to {chat_name}")

            # Call WhatsApp sender
            sender_script = Path(__file__).parent.parent.parent.parent / 'whatsapp-watcher' / 'scripts' / 'whatsapp_sender.py'

            if not sender_script.exists():
                logger.error(f"WhatsApp sender not found: {sender_script}")
                logger.warning("Please ensure whatsapp_sender.py exists")
                return False

            result = subprocess.run(
                [sys.executable, str(sender_script),
                 '--chat', chat_name,
                 '--message', message,
                 '--session-path', str(self.vault_path.parent / 'whatsapp_session')],
                capture_output=True, text=True, timeout=120
            )

            if result.returncode == 0:
                logger.info(f"✅ WhatsApp message sent to {chat_name}")
                return True
            else:
                logger.error(f"❌ WhatsApp send failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ WhatsApp send timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp: {e}")
            return False

    def execute_payment(self, metadata: Dict) -> bool:
        """Execute approved payment."""
        try:
            amount = metadata.get('amount')
            recipient = metadata.get('recipient')

            logger.info(f"Processing payment: {amount} to {recipient}")

            # Log payment for manual processing
            payment_log = self.logs / 'payments_pending.json'
            payments = []
            if payment_log.exists():
                payments = json.loads(payment_log.read_text())

            payments.append({
                "timestamp": datetime.now().isoformat(),
                "amount": amount,
                "recipient": recipient,
                "status": "pending_manual"
            })
            payment_log.write_text(json.dumps(payments, indent=2))

            logger.warning("⚠️  Payment logged for manual processing")
            return True

        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            return False

    def execute_social(self, metadata: Dict, content: str) -> bool:
        """Execute approved social post."""
        try:
            platform = metadata.get('platform')

            logger.info(f"Executing {platform} post")

            if platform == 'linkedin':
                # Call LinkedIn poster
                result = subprocess.run(
                    [sys.executable,
                     '.claude/skills/linkedin-poster/scripts/linkedin_poster.py',
                     '--vault-path', str(self.vault_path),
                     '--post'],
                    capture_output=True, text=True, timeout=120
                )

                if result.returncode == 0:
                    logger.info(f"✅ LinkedIn post executed")
                    return True
                else:
                    logger.error(f"❌ LinkedIn post failed: {result.stderr}")
                    return False
            else:
                logger.warning(f"Unknown platform: {platform}")
                return False

        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            return False

    def process_file(self, filepath: Path):
        """Process an approved file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            metadata = self.parse_frontmatter(content)

            action_type = metadata.get('action') or metadata.get('type')
            success = False

            logger.info(f"Processing approved action: {action_type} from {filepath.name}")

            if action_type == 'send_email':
                success = self.execute_email(metadata, content)
            elif action_type == 'whatsapp_message' or action_type == 'send_whatsapp':
                success = self.execute_whatsapp(metadata, content)
            elif action_type == 'payment':
                success = self.execute_payment(metadata)
            elif action_type == 'social_post':
                success = self.execute_social(metadata, content)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                # Try to infer from filename
                if 'EMAIL' in filepath.name.upper():
                    logger.info("Auto-detected email action from filename")
                    success = self.execute_email(metadata, content)
                elif 'WHATSAPP' in filepath.name.upper():
                    logger.info("Auto-detected WhatsApp action from filename")
                    success = self.execute_whatsapp(metadata, content)
                elif 'LINKEDIN' in filepath.name.upper():
                    logger.info("Auto-detected LinkedIn action from filename")
                    success = self.execute_social(metadata, content)

            # Log the action
            self.log_action(filepath, metadata, success)

            # Move to appropriate folder
            if success:
                done_path = self.done / filepath.name
                filepath.rename(done_path)
                logger.info(f"✅ Moved to Done: {done_path.name}")
            else:
                failed_path = self.failed / filepath.name
                filepath.rename(failed_path)
                logger.error(f"❌ Moved to Failed: {failed_path.name}")

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    def log_action(self, filepath: Path, metadata: Dict, success: bool):
        """Log the executed action."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": filepath.name,
            "action": metadata.get('action') or metadata.get('type'),
            "success": success,
            "metadata": metadata
        }

        log_file = self.logs / 'executed_approvals.json'

        try:
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = []

            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))

        except Exception as e:
            logger.error(f"Error logging action: {e}")

    def run_once(self):
        """Check for and process approved files."""
        if not self.approved.exists():
            return 0

        files = list(self.approved.glob('*.md'))
        if not files:
            logger.info("No approved files to process")
            return 0

        logger.info(f"Processing {len(files)} approved files...")

        count = 0
        for file_path in files:
            self.process_file(file_path)
            count += 1

        return count

    def run(self, interval: int = 30):
        """Run continuously."""
        logger.info(f"Starting Approval Monitor (checking every {interval}s)")

        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in monitor cycle: {e}")

            time.sleep(interval)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Approval Monitor')
    parser.add_argument('--vault-path', required=True, help='Path to vault')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=30, help='Check interval')

    args = parser.parse_args()

    monitor = ApprovalMonitor(vault_path=args.vault_path)

    if args.once:
        count = monitor.run_once()
        print(f"Processed {count} approved items")
    else:
        monitor.run(interval=args.interval)


if __name__ == '__main__':
    main()
