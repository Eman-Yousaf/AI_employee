---
updated: "2026-03-27T20:55:33.682357"
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
| Needs Action | 0 |
| Pending Approval | 0 |
| Approved | 2 |
| In Progress | 5 |
| Done | 9 |

## Recent Activity
- Last updated: 2026-03-27 20:55:33
- Items processed this session: 0
- Emails sent: 0
- LinkedIn posts: 0

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

## Components
- ✅ Gmail Watcher (monitors inbox)
- ✅ WhatsApp Watcher (monitors messages)
- ✅ LinkedIn Poster (with approval)
- ✅ Plan Creator (creates plans)
- ✅ Approval Workflow (HITL)
- ✅ Email MCP (sends emails)
