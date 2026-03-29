#!/usr/bin/env python3
"""Orchestrator - Complete Silver Tier Integration."""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SilverTierOrchestrator:
    """Complete Silver Tier orchestration."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.processes: Dict[str, subprocess.Popen] = {}

        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.in_progress = self.vault_path / 'In_Progress'
        self.rejected = self.vault_path / 'Rejected'

        # Ensure folders exist
        for folder in [self.needs_action, self.plans, self.approved, self.done,
                       self.pending_approval, self.in_progress, self.rejected]:
            folder.mkdir(parents=True, exist_ok=True)

        # Stats
        self.stats = {
            'items_processed': 0,
            'emails_sent': 0,
            'linkedin_posts': 0,
            'start_time': datetime.now().isoformat()
        }

        logger.info(f"Orchestrator initialized: {self.vault_path}")

    def update_dashboard(self):
        """Update Dashboard.md with current status."""
        try:
            dashboard = self.vault_path / 'Dashboard.md'

            # Count items in each folder
            counts = {
                'needs_action': len(list(self.needs_action.glob('*.md'))),
                'pending_approval': len(list(self.pending_approval.glob('*.md'))),
                'approved': len(list(self.approved.glob('*.md'))),
                'in_progress': len(list(self.in_progress.glob('*.md'))),
                'done': len(list(self.done.glob('*.md'))),
            }

            content = f"""---
updated: "{datetime.now().isoformat()}"
orchestrator: running
---

# AI Employee Dashboard

## System Status
| Component | Status |
|-----------|--------|
| Orchestrator | ✅ Running |
| Gmail Watcher | ✅ Available |
| WhatsApp Watcher | ✅ Available |
| LinkedIn Poster | ✅ Available |
| Email MCP | ✅ Available |

## Queue Status
| Folder | Count |
|--------|-------|
| Needs Action | {counts['needs_action']} |
| Pending Approval | {counts['pending_approval']} |
| Approved | {counts['approved']} |
| In Progress | {counts['in_progress']} |
| Done | {counts['done']} |

## Recent Activity
- Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Items processed this session: {self.stats['items_processed']}
- Emails sent: {self.stats['emails_sent']}
- LinkedIn posts: {self.stats['linkedin_posts']}

## Quick Actions

### Process All Pending Items
```bash
python orchestrator.py --vault-path ./vault --process-all
```

### Run Watchers (Once)
```bash
python orchestrator.py --vault-path ./vault --run-watchers
```

### Generate LinkedIn Post
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --vault-path ./vault --generate
```

## Silver Tier Components
- ✅ Gmail Watcher (monitors inbox)
- ✅ WhatsApp Watcher (monitors messages)
- ✅ LinkedIn Poster (with approval)
- ✅ Plan Creator (creates plans)
- ✅ Approval Workflow (HITL)
- ✅ Email MCP (sends emails)
"""

            dashboard.write_text(content, encoding='utf-8')
            logger.info("Dashboard updated")

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def run_plan_creator(self, item_path: Path) -> bool:
        """Run plan creator on a Needs_Action item."""
        script = '.claude/skills/plan-creator/scripts/create_plan.py'

        try:
            result = subprocess.run(
                [sys.executable, script, '--vault-path', str(self.vault_path), '--item', str(item_path)],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                logger.info(f"✅ Plan created for {item_path.name}")
                return True
            else:
                logger.error(f"❌ Plan creation failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error running plan creator: {e}")
            return False

    def run_approval_monitor(self) -> int:
        """Run approval monitor to execute approved items."""
        script = '.claude/skills/approval-workflow/scripts/monitor_approved.py'

        try:
            result = subprocess.run(
                [sys.executable, script, '--vault-path', str(self.vault_path), '--once'],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                # Parse output for counts
                output = result.stdout
                if 'email' in output.lower():
                    self.stats['emails_sent'] += 1
                if 'linkedin' in output.lower():
                    self.stats['linkedin_posts'] += 1

                logger.info("✅ Approval monitor processed items")
                return 1
            else:
                logger.error(f"❌ Approval monitor error: {result.stderr}")
                return 0

        except Exception as e:
            logger.error(f"❌ Error running approval monitor: {e}")
            return 0

    def run_gmail_watcher(self) -> int:
        """Run Gmail watcher once."""
        script = '.claude/skills/gmail-watcher/scripts/gmail_watcher.py'

        if not Path(script).exists():
            logger.warning(f"Gmail watcher not found: {script}")
            return 0

        try:
            result = subprocess.run(
                [sys.executable, script, '--vault-path', str(self.vault_path), '--once'],
                capture_output=True, text=True, timeout=60
            )

            # Parse output for new messages
            output = result.stdout + result.stderr
            new_items = output.count('Created EMAIL_') if 'Created EMAIL_' in output else 0

            if new_items > 0:
                logger.info(f"✅ Gmail watcher found {new_items} new messages")
            else:
                logger.info("Gmail watcher: no new messages")

            return new_items

        except Exception as e:
            logger.error(f"❌ Error running Gmail watcher: {e}")
            return 0

    def run_whatsapp_watcher(self) -> int:
        """Run WhatsApp watcher (requires manual login)."""
        script = '.claude/skills/whatsapp-watcher/scripts/whatsapp_watcher.py'

        if not Path(script).exists():
            logger.warning(f"WhatsApp watcher not found: {script}")
            return 0

        session_path = self.vault_path / '.whatsapp_session'

        try:
            result = subprocess.run(
                [sys.executable, script,
                 '--vault-path', str(self.vault_path),
                 '--session-path', str(session_path),
                 '--once'],
                capture_output=True, text=True, timeout=180
            )

            output = result.stdout + result.stderr
            new_items = output.count('Created WHATSAPP_') if 'Created WHATSAPP_' in output else 0

            if new_items > 0:
                logger.info(f"✅ WhatsApp watcher found {new_items} new messages")
            else:
                logger.info("WhatsApp watcher: no new messages (may need QR scan)")

            return new_items

        except subprocess.TimeoutExpired:
            logger.warning("WhatsApp watcher timed out (likely waiting for login)")
            return 0
        except Exception as e:
            logger.error(f"❌ Error running WhatsApp watcher: {e}")
            return 0

    def process_needs_action(self) -> int:
        """Process all items in Needs_Action folder."""
        items = list(self.needs_action.glob('*.md'))
        processed = 0

        if not items:
            logger.info("No items in Needs_Action")
            return 0

        logger.info(f"Processing {len(items)} items in Needs_Action")

        for item in items:
            try:
                # Create plan
                if self.run_plan_creator(item):
                    processed += 1
                    self.stats['items_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing {item.name}: {e}")

        return processed

    def process_approved(self) -> int:
        """Process all items in Approved folder."""
        items = list(self.approved.glob('*.md'))

        if not items:
            logger.info("No items in Approved folder")
            return 0

        logger.info(f"Processing {len(items)} approved items")
        return self.run_approval_monitor()

    def run_full_cycle(self):
        """Run one complete cycle of all watchers and processors."""
        logger.info("=" * 60)
        logger.info("Starting Full Cycle")
        logger.info("=" * 60)

        # Step 1: Check for new messages
        logger.info("\n📧 Step 1: Checking Gmail...")
        gmail_count = self.run_gmail_watcher()

        # Step 2: Process Needs_Action
        logger.info("\n📋 Step 2: Processing Needs Action...")
        action_count = self.process_needs_action()

        # Step 3: Process Approved items
        logger.info("\n✅ Step 3: Executing Approved Actions...")
        approved_count = self.process_approved()

        # Step 4: Update dashboard
        logger.info("\n📊 Step 4: Updating Dashboard...")
        self.update_dashboard()

        logger.info("\n" + "=" * 60)
        logger.info(f"Cycle Complete: {gmail_count} new emails, {action_count} plans, {approved_count} executed")
        logger.info("=" * 60)

        return {
            'gmail': gmail_count,
            'plans': action_count,
            'approved': approved_count
        }

    def run_watchers_only(self):
        """Run only watchers (no processing)."""
        logger.info("\n📧 Running Watchers...")
        gmail_count = self.run_gmail_watcher()

        # WhatsApp requires manual login, skip in auto mode
        logger.info("\n💬 WhatsApp: Run manually with: whatsapp_start.bat")

        self.update_dashboard()

        return {'gmail': gmail_count, 'whatsapp': 'manual'}

    def run_continuous(self, interval: int = 300):
        """Run orchestrator continuously."""
        logger.info("=" * 60)
        logger.info("Silver Tier Orchestrator - Continuous Mode")
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Check interval: {interval}s")
        logger.info("=" * 60)

        try:
            while True:
                self.run_full_cycle()
                logger.info(f"\n⏳ Sleeping {interval}s...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n\nShutting down...")
            self.update_dashboard()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Silver Tier Orchestrator')
    parser.add_argument('--vault-path', default='./vault', help='Path to vault')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=300, help='Check interval (seconds)')
    parser.add_argument('--process-all', action='store_true', help='Process all pending items')
    parser.add_argument('--run-watchers', action='store_true', help='Run watchers only')
    parser.add_argument('--dashboard', action='store_true', help='Update dashboard only')

    args = parser.parse_args()

    orchestrator = SilverTierOrchestrator(vault_path=args.vault_path)

    if args.dashboard:
        orchestrator.update_dashboard()
        print("✅ Dashboard updated")

    elif args.run_watchers:
        results = orchestrator.run_watchers_only()
        print(f"\nResults: {results}")

    elif args.process_all:
        orchestrator.run_full_cycle()

    elif args.continuous:
        orchestrator.run_continuous(interval=args.interval)

    else:
        # Default: one full cycle
        orchestrator.run_full_cycle()


if __name__ == '__main__':
    main()
