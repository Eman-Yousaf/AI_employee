# AI Employee

An agentic assistant that watches Gmail, WhatsApp and LinkedIn, drafts the work those
messages imply, and routes anything consequential through a human before it leaves your
machine. Built from nine [Claude Code](https://claude.com/claude-code) skills over an
[Obsidian](https://obsidian.md) vault. Local-first: no server, no database, no hosted
state.

## Drafting and sending are separate paths

The component that can actually send — `approval-workflow/scripts/monitor_approved.py` —
reads from exactly one directory, `vault/Approved/`. The watchers and generators that the
model drives write to exactly one other, `vault/Pending_Approval/`. Nothing in the
drafting path can reach the executor's input:

```
watchers/generators ──► Pending_Approval/ ──► [ you move the file ] ──► Approved/ ──► executor ──► Done/
                                                                                          │
                                                                                          └─► Logs/approvals.json
```

An approval request is a Markdown file with the action in its frontmatter, so what you are
approving is legible before you approve it — recipient, amount, and body are all on screen
as plain text:

```markdown
---
type: approval_request
action: payment
amount: 1500.00
currency: USD
recipient: Client A
recipient_account: XXXX1234
---
```

Approving is dragging that file into `Approved/`. Rejecting is dragging it into
`Rejected/`, or deleting it. Every executed action is appended to `Logs/approvals.json`
and the file lands in `Done/`, so the vault is its own audit trail.

To be precise about what this does and does not guarantee: it is a separation of paths,
not a sandbox. An agent with write access to the vault could move a file into `Approved/`
itself. The boundary holds because the executor's input directory is kept out of the
drafting workflow, not because the filesystem forbids it — worth knowing if you extend
this to actions where the failure is expensive.

## Skills

| Skill | What it does |
|---|---|
| `approval-workflow` | Creates approval requests; monitors `Approved/` and executes email, WhatsApp, payment and social actions |
| `gmail-watcher` | Polls Gmail over IMAP and the API for unread/important mail, writes action files into the vault |
| `whatsapp-watcher` | Watches WhatsApp Web via Playwright for messages matching keywords |
| `linkedin-poster` | Generates post drafts and publishes approved ones through a persistent browser session |
| `email-mcp` | MCP server exposing send/draft/read/search over Gmail |
| `plan-creator` | Turns items in `Needs_Action/` into structured plans with steps and dependencies |
| `reasoning-loop` | Persistence pattern that keeps multi-step tasks running to completion |
| `cron-scheduler` | Recurring jobs — daily briefings, periodic watcher runs |
| `browsing-with-playwright` | Shared browser automation used by the WhatsApp and LinkedIn skills |

`orchestrator.py` ties them together: `run_full_cycle()` runs the watchers, plan creator
and approval monitor once; `run_continuous(interval=300)` loops them.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

**Gmail** — create an OAuth client in Google Cloud Console, download the JSON to
`config/credentials.json` (`config/credentials.json.template` shows the shape), then run
`Gmail_Auth.bat` to complete the consent flow and write `config/token.json`.

**WhatsApp** — run `WhatsApp_Setup.bat` and scan the QR code. The session persists.

**LinkedIn** — the first post opens a real browser window (`headless=False`). Log in when
it appears; the session is stored in `vault/.linkedin_session` and reused after that.

Then `Start_Auto_Processing.bat` to run continuously, or `Execute_Approved.bat` to process
the approval queue once.

| Script | Purpose |
|---|---|
| `Start_Auto_Processing.bat` | Run the full cycle continuously |
| `Execute_Approved.bat` | Process the approval queue once |
| `SEND_NOW.bat` | Integration test harness — **writes straight to `Approved/` and skips review** |
| `Gmail_Auth.bat` | Gmail OAuth consent flow |
| `WhatsApp_Setup.bat` | WhatsApp Web QR pairing |
| `Test_All_Setup.bat` | Check every configured integration |

## Vault layout

```
vault/
├── Needs_Action/      # what the watchers found
├── Pending_Approval/  # drafted, awaiting you
├── Approved/          # you moved it here; the executor picks it up
├── Rejected/          # you moved it here instead
├── Done/              # executed, with outcome
├── Templates/         # frontmatter templates for each action type
└── Logs/              # approvals.json audit trail
```

Only `Templates/`, `Company_Handbook.md` and `Business_Goals.md` are in version control.
Every other folder above is runtime state — real mail, real contacts — and is gitignored;
the scripts create the directories on first run. The frontmatter `action:` field
(`send_email`, `send_whatsapp`, `social_post`) is what routes an approved file to the
right executor.

The one exception to the separation above is `SEND_NOW.bat`, which writes directly into
`Approved/` to test that an integration works. It says so when you run it.

## Credentials

`config/` is gitignored apart from the template. Supply your own OAuth client and app
password; nothing in this repo ships working credentials, and none should be committed.
