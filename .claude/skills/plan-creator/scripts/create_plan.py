#!/usr/bin/env python3
"""Plan Creator - Creates structured Plan.md files from action items."""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ActionItem:
    """Represents an action item."""
    file_path: Path
    item_type: str
    source: str
    subject: str
    priority: str
    metadata: Dict


class PlanCreator:
    """Creates plans from action items."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.in_progress = self.vault_path / 'In_Progress'

        # Ensure directories exist
        self.plans.mkdir(parents=True, exist_ok=True)
        self.in_progress.mkdir(parents=True, exist_ok=True)

        # Priority keywords
        self.keywords = {
            'urgent': ['urgent', 'emergency', 'asap', 'critical'],
            'high': ['invoice', 'payment', 'deadline', 'meeting', 'call'],
            'medium': ['question', 'follow-up', 'review'],
            'low': ['fyi', 'notification', 'update']
        }

        logger.info(f"PlanCreator initialized with vault: {self.vault_path}")

    def parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown file."""
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

                    # Try to parse as list
                    if value.startswith('[') and value.endswith(']'):
                        try:
                            value = json.loads(value.replace("'", '"'))
                        except:
                            value = value[1:-1].split(',')
                            value = [v.strip().strip('"\'') for v in value]

                    metadata[key] = value

            return metadata

        except Exception as e:
            logger.error(f"Error parsing frontmatter: {e}")
            return {}

    def load_action_item(self, file_path: Path) -> Optional[ActionItem]:
        """Load an action item from file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            metadata = self.parse_frontmatter(content)

            return ActionItem(
                file_path=file_path,
                item_type=metadata.get('type', 'unknown'),
                source=metadata.get('source', 'unknown'),
                subject=metadata.get('subject', 'No Subject'),
                priority=metadata.get('priority', 'medium'),
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error loading action item {file_path}: {e}")
            return None

    def get_action_items(self) -> List[ActionItem]:
        """Get all unprocessed action items."""
        items = []

        if not self.needs_action.exists():
            return items

        for file_path in self.needs_action.glob('*.md'):
            item = self.load_action_item(file_path)
            if item:
                items.append(item)

        return items

    def check_existing_plan(self, item: ActionItem) -> bool:
        """Check if a plan already exists for this action item."""
        base_name = item.file_path.stem
        plan_file = self.plans / f"PLAN_{base_name}.md"
        return plan_file.exists()

    def create_email_plan(self, item: ActionItem) -> str:
        """Create a plan for email response."""
        from_email = item.metadata.get('from_email', 'unknown@example.com')
        subject = item.metadata.get('subject', 'No Subject')

        return f"""# Plan: Respond to Email

## Objective
Draft and send response to email from {from_email}.

## Context
- **From:** {item.metadata.get('from_name', 'Unknown')}
- **Subject:** {subject}
- **Priority:** {item.priority}

## Steps

### Phase 1: Analysis
- [ ] Read full email content
- [ ] Check if sender is in known contacts
- [ ] Determine response type (reply/info/action needed)

### Phase 2: Draft
- [ ] Draft response message
- [ ] Check tone and professionalism
- [ ] Verify facts and details

### Phase 3: Approval
- [ ] {{if new_contact}} Create approval request
- [ ] {{if sensitive}} Get approval before sending

### Phase 4: Send
- [ ] Send via Email MCP
- [ ] Log to email activity
- [ ] Update Dashboard

## Dependencies
- Needs: Sender information from contacts
- Blockers: None

## Approval Required
{{if new_contact or sensitive}}
- [ ] Email send approval required
{{else}}
- Auto-approve (known contact)
{{endif}}

## Notes
Keywords detected: {item.metadata.get('keywords_found', [])}
Source file: {item.file_path.name}
"""

    def create_whatsapp_plan(self, item: ActionItem) -> str:
        """Create a plan for WhatsApp message."""
        chat_name = item.metadata.get('chat_name', 'Unknown')

        return f"""# Plan: Process WhatsApp Message

## Objective
Review and respond to WhatsApp message from {chat_name}.

## Context
- **Chat:** {chat_name}
- **Priority:** {item.priority}
- **Unread Count:** {item.metadata.get('unread_count', 1)}

## Steps

### Phase 1: Review
- [ ] Open WhatsApp Web to read full message
- [ ] Check message context and history
- [ ] Identify if business-related

### Phase 2: Analyze
- [ ] Determine if invoice/payment related
- [ ] Check for urgent requests
- [ ] Identify action needed

### Phase 3: Action
- [ ] {{if invoice_needed}} Create invoice task
- [ ] {{if urgent}} Create immediate response plan
- [ ] {{if question}} Research answer

### Phase 4: Response
- [ ] Draft reply (if needed)
- [ ] Send via WhatsApp Web (manual)
- [ ] Update Dashboard
- [ ] Log to activity

## Dependencies
- Needs: Full message content from WhatsApp
- Blockers: None

## Notes
Message preview: {item.metadata.get('message_preview', 'N/A')}
Keywords: {item.metadata.get('keywords_found', [])}
Source file: {item.file_path.name}
"""

    def create_default_plan(self, item: ActionItem) -> str:
        """Create a default/generic plan."""
        return f"""# Plan: Process Action Item

## Objective
Process action item: {item.subject}

## Context
- **Type:** {item.item_type}
- **Source:** {item.source}
- **Priority:** {item.priority}

## Steps

### Phase 1: Analysis
- [ ] Review action item details
- [ ] Understand requirements
- [ ] Identify dependencies

### Phase 2: Planning
- [ ] Break down into steps
- [ ] Estimate time required
- [ ] Check for blockers

### Phase 3: Execution
- [ ] Execute steps
- [ ] Document progress
- [ ] Handle any issues

### Phase 4: Completion
- [ ] Verify task complete
- [ ] Update Dashboard
- [ ] Move to Done
- [ ] Log activity

## Dependencies
- None identified

## Approval Required
- Check Company_Handbook.md

## Notes
Source file: {item.file_path.name}
Metadata: {json.dumps(item.metadata, indent=2)}
"""

    def generate_plan_content(self, item: ActionItem) -> str:
        """Generate appropriate plan content based on item type."""
        if item.item_type == 'email':
            return self.create_email_plan(item)
        elif item.item_type == 'whatsapp_message':
            return self.create_whatsapp_plan(item)
        else:
            return self.create_default_plan(item)

    def create_plan(self, item: ActionItem) -> Optional[Path]:
        """Create a plan file for an action item."""
        if self.check_existing_plan(item):
            logger.info(f"Plan already exists for {item.file_path.name}")
            return None

        # Generate plan content
        plan_content = self.generate_plan_content(item)

        # Create plan file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = item.file_path.stem
        plan_filename = f"PLAN_{base_name}_{timestamp}.md"
        plan_path = self.plans / plan_filename

        # Add frontmatter
        full_content = f"""---
type: plan
source_item: {item.file_path.name}
item_type: {item.item_type}
priority: {item.priority}
status: active
created: "{datetime.now().isoformat()}"
---

{plan_content}
"""

        plan_path.write_text(full_content, encoding='utf-8')
        logger.info(f"Created plan: {plan_path.name}")

        # Move action item to In_Progress
        dest_path = self.in_progress / item.file_path.name
        try:
            item.file_path.rename(dest_path)
            logger.info(f"Moved action item to In_Progress: {dest_path.name}")
        except Exception as e:
            logger.error(f"Error moving action item: {e}")

        return plan_path

    def run(self, single: bool = False):
        """Process all action items and create plans."""
        items = self.get_action_items()
        logger.info(f"Found {len(items)} action items to process")

        created = 0
        for item in items:
            try:
                plan_path = self.create_plan(item)
                if plan_path:
                    created += 1
                    print(f"Created: {plan_path.name}")

                if single:
                    break

            except Exception as e:
                logger.error(f"Error creating plan for {item.file_path}: {e}")

        logger.info(f"Created {created} plans")
        return created


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Plan Creator')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--item', help='Process specific action item file')
    parser.add_argument('--single', action='store_true', help='Process only one item')

    args = parser.parse_args()

    creator = PlanCreator(vault_path=args.vault_path)

    if args.item:
        item_path = Path(args.item)
        if item_path.exists():
            item = creator.load_action_item(item_path)
            if item:
                creator.create_plan(item)
        else:
            print(f"File not found: {args.item}")
    else:
        creator.run(single=args.single)


if __name__ == '__main__':
    main()
