---
name: plan-creator
description: |
  Create structured Plan.md files from action items in /Needs_Action.
  Breaks down tasks into steps, identifies dependencies, and suggests actions.
  Core component of the Claude reasoning loop for autonomous task completion.
  Use for task planning, project management, and workflow automation.
---

# Plan Creator

Creates structured Plan.md files from action items in `/Needs_Action/`.

## Overview

The Plan Creator is the core of Claude's reasoning capability. When items appear in `/Needs_Action/`, this skill:

1. Analyzes the action item
2. Breaks it down into executable steps
3. Identifies dependencies and blockers
4. Creates a Plan.md with checkboxes
5. Determines if approval is needed

## How It Works

```
/Needs_Action/ITEM_xxx.md → [Plan Creator] → /Plans/PLAN_xxx.md
```

## Plan File Format

```markdown
---
type: plan
source: EMAIL_client_2026-01-07T103000
status: active
created: 2026-01-07T10:35:00Z
priority: high
estimated_duration: 30m
---

# Plan: Send Invoice to Client A

## Objective
Generate and send January 2026 invoice to Client A for $1,500.

## Context
- Client requested invoice via email
- Monthly retainer: $1,500
- Due date: Net 15

## Steps

### Phase 1: Preparation
- [x] Identify client details from CRM
- [x] Confirm billing amount from /Accounting/Rates.md
- [ ] Generate invoice PDF
  - Depends on: Invoice template
  - Blocker: None

### Phase 2: Approval
- [ ] Create approval request for email send
  - Depends on: Invoice generation
  - Blocker: Requires human approval for attachments

### Phase 3: Execution
- [ ] Send email via Email MCP
  - Depends on: Approval received
  - Blocker: Waiting for /Approved/ trigger
- [ ] Log transaction in /Accounting/
- [ ] Update Dashboard.md

## Dependencies
| Step | Depends On | Status |
|------|------------|--------|
| 3 | Step 2 | blocked |
| 4 | Approval | blocked |

## Approval Required
- [ ] Email send with attachment (sensitive)

## Notes
- Client prefers PDF attachments
- CC: accounting@company.com
- Reference: Monthly retainer agreement
```

## Usage

### Manual Trigger

```bash
# Create plan for specific action item
python scripts/create_plan.py --action-file /Needs_Action/EMAIL_xxx.md

# Create plans for all pending action items
python scripts/create_plan.py --all
```

### Automatic Trigger

The orchestrator automatically runs:

```bash
# When new files appear in /Needs_Action/
claude "Create plans for all items in /Needs_Action that don't have plans yet"
```

## Integration with Ralph Wiggum Loop

The Plan Creator enables the Ralph Wiggum persistence pattern:

1. Watcher creates action file
2. Plan Creator creates Plan.md
3. Ralph Wiggum loop starts: "Execute plan until complete"
4. Claude works through steps, checking boxes
5. On exit attempt, Ralph checks: "Any unchecked boxes?"
6. If yes → Re-inject prompt to continue
7. If no → Task complete, move to /Done/

## Step Status Values

| Status | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[-]` | In progress |
| `[x]` | Complete |
| `[b]` | Blocked (has dependency) |
| `[a]` | Requires approval |
| `[!]` | Failed (needs attention) |

## Priority Levels

| Level | Criteria | Action |
|-------|----------|--------|
| critical | Keywords: "urgent", "asap", "emergency" | Immediate notification |
| high | Keywords: "invoice", "payment", "deadline" | Process within 1 hour |
| medium | Standard business requests | Process within 4 hours |
| low | FYI, notifications | Process within 24 hours |

## Plan Templates

### Email Response Plan

```markdown
## Steps
- [ ] Analyze email content and intent
- [ ] Check sender in known contacts
- [ ] Draft response
- [ ] Review for tone and accuracy
- [ ] {if sensitive} Create approval request
- [ ] {if approved} Send via Email MCP
- [ ] Log to /Logs/email_activity.json
```

### Invoice Plan

```markdown
## Steps
- [ ] Confirm client billing rate
- [ ] Calculate amount for period
- [ ] Generate PDF using template
- [ ] Create approval request
- [ ] {on approval} Send via Email MCP
- [ ] Log transaction
- [ ] Update Dashboard.md
```

### Social Media Plan

```markdown
## Steps
- [ ] Generate content from source
- [ ] Check against Company_Handbook.md guidelines
- [ ] Create approval request
- [ ] {on approval} Schedule via LinkedIn MCP
- [ ] Log to /Logs/social_activity.json
```

## Configuration

Create `config/plan_creator.json`:

```json
{
  "vault_path": "/path/to/AI_Employee_Vault",
  "auto_create": true,
  "templates": {
    "email": "templates/plan_email.md",
    "invoice": "templates/plan_invoice.md",
    "social": "templates/plan_social.md",
    "default": "templates/plan_default.md"
  },
  "approval_thresholds": {
    "payment": 0,
    "email_external": 0,
    "email_internal": 50,
    "social_post": 0,
    "file_delete": 0
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plans not created | Check auto_create setting, verify vault path |
| Steps unclear | Review and update Company_Handbook.md with examples |
| Dependencies wrong | Manually edit Plan.md to correct dependencies |
| Approval not triggered | Check approval_thresholds config |

## Best Practices

1. **Keep steps atomic** - Each checkbox should be completable in one action
2. **Use dependencies** - Don't overwhelm with too many parallel tasks
3. **Estimate duration** - Helps with scheduling and prioritization
4. **Log blockers** - When a step can't complete, document why
5. **Update context** - As new info arrives, update the plan
