---
action: send_email
to: ""
subject: ""
is_html: false
priority: medium
created: "{{date:YYYY-MM-DD}}T{{time:HH:mm:ss}}"
status: pending_approval
---

# Email Approval

**To:** {{to}}
**Subject:** {{subject}}
**Priority:** {{priority}}

## Body

{{body}}

---

## Instructions

To **APPROVE** this email:
1. Review the content above
2. Move this file to `Approved/` folder (drag and drop in Obsidian)
3. The system will automatically send it

To **REJECT** this email:
1. Move this file to `Rejected/` folder

---
*Created by AI Employee*
