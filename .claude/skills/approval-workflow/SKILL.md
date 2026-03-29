---
name: approval-workflow
description: |
  Human-in-the-loop (HITL) approval system for sensitive actions.
  Creates approval request files, monitors /Approved folder, and executes actions after human verification.
  Required for payments, external emails, social posts, and file deletions.
  Use for safety, compliance, and preventing AI errors.
---

# Approval Workflow

Human-in-the-loop (HITL) system for sensitive AI actions.

## Overview

The Approval Workflow ensures humans review and approve sensitive actions before execution:

```
AI Detects Action → Creates Approval File → Human Reviews → Moves to /Approved/ → Action Executes
```

## Why HITL Matters

| Action | Risk Without HITL | HITL Benefit |
|--------|-------------------|--------------|
| Payment | Wrong recipient, wrong amount | Visual verification before money moves |
| External Email | Wrong client, wrong content | Review tone and facts |
| Social Post | Brand damage, PR issue | Ensure message aligns with brand |
| File Delete | Data loss | Confirm deletion is intentional |
| LinkedIn Post | Professional reputation | Review public content |

## Folder Structure

```
/Vault/
├── Pending_Approval/    # AI creates requests here
│   ├── PAYMENT_xxx.md
│   ├── EMAIL_xxx.md
│   └── SOCIAL_xxx.md
├── Approved/            # Human moves files here to approve
│   └── (moved files)
├── Rejected/            # Human moves files here to reject
│   └── (moved files)
└── Logs/
    └── approvals.json
```

## Approval Request Format

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: 1500.00
currency: USD
recipient: Client A
recipient_account: XXXX1234
reason: January 2026 retainer payment
invoice_ref: INV-2026-001
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

# Payment Approval Request

## Payment Details
| Field | Value |
|-------|-------|
| Amount | $1,500.00 |
| To | Client A |
| Account | ****1234 |
| Reason | Invoice #1234 - January retainer |
| Due Date | 2026-01-15 |

## Source
- From Plan: /Plans/PLAN_invoice_client_a.md
- Triggered by: WhatsApp message request

## To Approve
**Move this file to `/Approved/` folder**

## To Reject
**Move this file to `/Rejected/` folder**

## Notes
- Payment will be initiated via Banking MCP
- Confirmation will be logged to /Logs/payments.json
- This request expires in 24 hours
```

### Email Approval

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: "January Invoice - $1,500"
attachment: /Vault/Invoices/2026-01_client.pdf
has_attachment: true
sensitive: false
created: 2026-01-07T10:30:00Z
---

# Email Approval Request

## Preview

**To:** client@example.com
**Subject:** January Invoice - $1,500
**Attachment:** 2026-01_client.pdf

**Body:**
> Hi [Client],
>
> Please find attached your invoice for January 2026 services.
>
> Amount: $1,500.00
> Due Date: January 15, 2026
>
> Best regards,
> AI Employee on behalf of [Your Name]

## To Approve
Move to `/Approved/`

## To Edit
1. Move to `/Rejected/`
2. Edit source file in `/Plans/`
3. Re-run plan creation
```

### Social Post Approval

```markdown
---
type: approval_request
action: linkedin_post
scheduled: 2026-01-08T09:00:00Z
topic: "AI consulting launch"
tone: professional
hashtags: ["#AI", "#Consulting"]
---

# LinkedIn Post Approval

## Generated Post

Just launched our AI consulting service!

We help businesses automate repetitive tasks and reclaim 10+ hours per week.

If you're drowning in manual work, let's chat.

Comment "AI" below 👇

#AI #Automation #BusinessGrowth

---

## Platform
LinkedIn (Professional Network)

## Scheduled
January 8, 2026 at 9:00 AM

## To Approve
Move to `/Approved/` by 8:45 AM for scheduled posting
```

## Workflow

### Creating Approval Requests

When AI detects a sensitive action:

```python
# In plan execution
def create_approval_request(action_type, details):
    approval_file = vault / "Pending_Approval" / f"{action_type}_{timestamp}.md"

    content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
---

{format_details(details)}

## To Approve
Move this file to `/Approved/`

## To Reject
Move this file to `/Rejected/`
"""

    approval_file.write_text(content)
    return approval_file
```

### Monitoring Approved Folder

```python
# watcher/approval_monitor.py
class ApprovalMonitor:
    def __init__(self, vault_path):
        self.approved_path = Path(vault_path) / "Approved"
        self.orchestrator = Orchestrator()

    def on_file_created(self, event):
        approval_file = Path(event.src_path)
        action = self.parse_approval(approval_file)

        # Execute the approved action
        self.orchestrator.execute(action)

        # Move to Done
        approval_file.rename(
            Path(self.vault_path) / "Done" / approval_file.name
        )
```

### Timeouts and Expiration

Approval requests expire to prevent stale actions:

```python
# Check for expired approvals
def check_expired_approvals():
    pending = Path("Pending_Approval").glob("*.md")

    for file in pending:
        metadata = parse_frontmatter(file)
        expires = metadata.get("expires")

        if expires and datetime.now() > parse(expires):
            # Move to Rejected with expiration note
            move_to_rejected(file, reason="Expired")
            notify_human(f"Approval request expired: {file.name}")
```

## Auto-Approve Rules

Configure low-risk actions to skip approval:

```json
{
  "auto_approve": {
    "email_internal": true,
    "email_known_contacts": ["partner@company.com"],
    "amount_threshold": 50,
    "recurring_payments": ["AWS", "GitHub", "Notion"]
  }
}
```

## Notification Methods

When approval is needed, notify via:

1. **Dashboard.md update** - Real-time status
2. **System notification** - Desktop alert
3. **Email summary** - Daily digest of pending approvals
4. **WhatsApp alert** - For urgent items

```python
def notify_approval_needed(approval_file):
    # Update dashboard
    update_dashboard(approval_file)

    # Send notification if urgent
    if is_urgent(approval_file):
        send_notification("Urgent approval needed", approval_file)
```

## Audit Trail

Log all approval activity:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "payment",
  "requested_by": "claude_code",
  "approved_by": "human",
  "approval_time": "2026-01-07T10:35:00Z",
  "execution_time": "2026-01-07T10:36:00Z",
  "result": "success",
  "amount": 1500.00
}
```

## Configuration

Create `config/approval_workflow.json`:

```json
{
  "expiration_hours": 24,
  "notification_channels": ["dashboard", "desktop", "email"],
  "urgent_keywords": ["urgent", "asap", "payment", "deadline"],
  "auto_approve": {
    "enabled": false,
    "internal_emails": true,
    "max_amount": 0
  }
}
```

## Best Practices

1. **Review within 4 hours** - Don't let requests pile up
2. **Check source plan** - Understand context before approving
3. **Reject with notes** - Explain why for future improvements
4. **Never auto-approve payments** - Always verify
5. **Keep audit logs** - Retain for 90+ days
