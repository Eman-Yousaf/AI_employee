#!/usr/bin/env python3
"""Approval Workflow - Creates approval requests for sensitive actions."""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApprovalWorkflow:
    """Manages human-in-the-loop approval process."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for path in [self.pending, self.approved, self.rejected, self.logs]:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"ApprovalWorkflow initialized")

    def create_email_approval(self, to: str, subject: str, body: str,
                             source_plan: str = None, reason: str = None) -> Path:
        """Create approval request for email send."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_to = ''.join(c for c in to if c.isalnum() or c in ('@', '.', '_'))
        filename = f"EMAIL_{safe_to}_{timestamp}.md"
        filepath = self.pending / filename

        expire_time = datetime.now() + timedelta(hours=24)

        content = f"""---
type: approval_request
action: send_email
to: "{to}"
subject: "{subject}"
created: "{datetime.now().isoformat()}"
expires: "{expire_time.isoformat()}"
status: pending
source_plan: "{source_plan or 'N/A'}"
---

# Email Approval Request

## Preview

**To:** {to}
**Subject:** {subject}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Body
```
{body[:500]}
{'... (truncated)' if len(body) > 500 else ''}
```

## Reason for Approval
{reason or "This email requires human approval before sending."}

## To Approve
**Move this file to `/Approved/` folder**

The email will be sent automatically when moved.

## To Reject
**Move this file to `/Rejected/` folder**

The email will NOT be sent. Review the source plan and try again.

## Safety Notes
- Double-check recipient address
- Verify subject line accuracy
- Confirm no sensitive information exposed
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created email approval request: {filepath.name}")
        return filepath

    def create_payment_approval(self, amount: float, currency: str, recipient: str,
                               reason: str, invoice_ref: str = None) -> Path:
        """Create approval request for payment."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_recipient = ''.join(c for c in recipient if c.isalnum() or c == '_')[:20]
        filename = f"PAYMENT_{safe_recipient}_{timestamp}.md"
        filepath = self.pending / filename

        expire_time = datetime.now() + timedelta(hours=48)

        content = f"""---
type: approval_request
action: payment
amount: {amount}
currency: "{currency}"
recipient: "{recipient}"
reason: "{reason}"
invoice_ref: "{invoice_ref or 'N/A'}"
created: "{datetime.now().isoformat()}"
expires: "{expire_time.isoformat()}"
status: pending
---

# Payment Approval Request

⚠️ **FINANCIAL ACTION REQUIRES APPROVAL**

## Payment Details

| Field | Value |
|-------|-------|
| **Amount** | {currency} {amount:,.2f} |
| **To** | {recipient} |
| **Reason** | {reason} |
| **Invoice** | {invoice_ref or 'N/A'} |

## ⚠️ IMPORTANT

**Verify before approving:**
- [ ] Recipient bank details are correct
- [ ] Amount matches invoice/expectation
- [ ] Payment is authorized in budget
- [ ] No duplicate payments

## To Approve
**Move this file to `/Approved/` folder**

Payment will be initiated immediately upon approval.

## To Reject
**Move this file to `/Rejected/` folder**

Include reason in notes below.

## Rejection Notes
_(Add notes here if rejecting)_

## Audit Trail
- Created: {datetime.now().isoformat()}
- Expires: {expire_time.isoformat()}
- Request ID: PAY-{timestamp}
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created payment approval request: {filepath.name}")
        return filepath

    def create_social_approval(self, platform: str, content: str,
                               scheduled_time: str = None) -> Path:
        """Create approval request for social media post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SOCIAL_{platform.upper()}_{timestamp}.md"
        filepath = self.pending / filename

        expire_time = datetime.now() + timedelta(hours=12)

        content = f"""---
type: approval_request
action: social_post
platform: "{platform}"
scheduled_time: "{scheduled_time or 'ASAP'}"
created: "{datetime.now().isoformat()}"
expires: "{expire_time.isoformat()}"
status: pending
---

# Social Media Post Approval

**Platform:** {platform}
**Scheduled:** {scheduled_time or 'ASAP (when approved)'}

## Post Content

```
{content}
```

## Check Before Approving

- [ ] No confidential information included
- [ ] Tone matches company brand
- [ ] No spelling/grammar errors
- [ ] No controversial statements
- [ ] Hashtags are appropriate
- [ ] Links work (if included)

## To Approve
**Move this file to `/Approved/` folder**

Post will be scheduled/sent based on the scheduled_time.

## To Reject
**Move this file to `/Rejected/` folder**

Edit the source content and regenerate if needed.

## Notes
_Review against Company_Handbook.md guidelines_
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created social approval request: {filepath.name}")
        return filepath

    def log_approval_action(self, approval_file: Path, action: str, details: Dict):
        """Log approval action to audit log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "approval_file": approval_file.name,
            "action": action,
            "details": details
        }

        log_file = self.logs / 'approvals.json'

        try:
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = []

            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))

        except Exception as e:
            logger.error(f"Error logging approval: {e}")


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Create Approval Request')
    parser.add_argument('--vault-path', required=True, help='Path to vault')
    parser.add_argument('--type', choices=['email', 'payment', 'social'],
                        required=True, help='Approval type')

    # Email args
    parser.add_argument('--to', help='Email recipient')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')

    # Payment args
    parser.add_argument('--amount', type=float, help='Payment amount')
    parser.add_argument('--currency', default='USD', help='Currency')
    parser.add_argument('--recipient', help='Payment recipient')
    parser.add_argument('--reason', help='Payment reason')
    parser.add_argument('--invoice-ref', help='Invoice reference')

    # Social args
    parser.add_argument('--platform', help='Social platform')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--scheduled-time', help='When to post')

    args = parser.parse_args()

    workflow = ApprovalWorkflow(vault_path=args.vault_path)

    if args.type == 'email':
        if not all([args.to, args.subject, args.body]):
            print("Error: --to, --subject, and --body required for email")
            return 1

        filepath = workflow.create_email(
            to=args.to,
            subject=args.subject,
            body=args.body
        )
        print(f"Created: {filepath}")

    elif args.type == 'payment':
        if not all([args.amount, args.recipient, args.reason]):
            print("Error: --amount, --recipient, and --reason required for payment")
            return 1

        filepath = workflow.create_payment_approval(
            amount=args.amount,
            currency=args.currency,
            recipient=args.recipient,
            reason=args.reason,
            invoice_ref=args.invoice_ref
        )
        print(f"Created: {filepath}")

    elif args.type == 'social':
        if not all([args.platform, args.content]):
            print("Error: --platform and --content required for social")
            return 1

        filepath = workflow.create_social_approval(
            platform=args.platform,
            content=args.content,
            scheduled_time=args.scheduled_time
        )
        print(f"Created: {filepath}")

    return 0


if __name__ == '__main__':
    exit(main())
