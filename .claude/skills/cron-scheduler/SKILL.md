---
name: cron-scheduler
description: |
  Schedule recurring AI tasks using cron (Linux/Mac) or Task Scheduler (Windows).
  Supports daily briefings, weekly audits, hourly watchers, and custom schedules.
  Use for automated reports, periodic data sync, and scheduled social posts.
---

# Cron Scheduler

Schedule recurring tasks for your AI Employee using cron or Task Scheduler.

## Overview

The Cron Scheduler enables time-based automation:

| Schedule | Example Tasks |
|----------|--------------|
| Every minute | Watcher scripts, file monitors |
| Hourly | Inbox triage, data sync |
| Daily | Morning briefing, daily reports |
| Weekly | CEO audit, weekly reviews |
| Monthly | Accounting reconciliation |

## Platform Differences

### Linux/Mac (Cron)

Use system `crontab` for scheduling.

### Windows (Task Scheduler)

Use `schtasks` command or Task Scheduler GUI.

## Setup

### Linux/Mac

```bash
# Edit crontab
crontab -e

# Add entries (see examples below)
```

### Windows

```powershell
# Using schtasks (command line)
schtasks /create /tn "AIEmployee-DailyBriefing" /tr "python C:\path\to\briefing.py" /sc daily /st 08:00

# Or use Task Scheduler GUI:
# 1. Open Task Scheduler
# 2. Create Basic Task
# 3. Set trigger (daily, weekly, etc.)
# 4. Set action (run python script)
```

## Common Schedules

### Daily Morning Briefing (8 AM)

**Linux/Mac:**
```cron
# Run daily at 8:00 AM
0 8 * * * cd /path/to/AI_employee && python scripts/daily_briefing.py --vault-path /path/to/vault
```

**Windows:**
```powershell
schtasks /create /tn "AIEmployee-Briefing" /tr "python C:\path\to\scripts\daily_briefing.py" /sc daily /st 08:00
```

### Weekly CEO Audit (Sunday 11 PM)

**Linux/Mac:**
```cron
# Run every Sunday at 11:00 PM
0 23 * * 0 cd /path/to/AI_employee && python scripts/weekly_audit.py --vault-path /path/to/vault
```

**Windows:**
```powershell
schtasks /create /tn "AIEmployee-WeeklyAudit" /tr "python C:\path\to\scripts\weekly_audit.py" /sc weekly /d SUN /st 23:00
```

### Gmail Watcher (Every 2 minutes)

**Linux/Mac:**
```cron
# Run every 2 minutes
*/2 * * * * cd /path/to/AI_employee && python scripts/gmail_watcher.py --check-once --vault-path /path/to/vault
```

**Windows:**
```powershell
# Task Scheduler can't do every 2 minutes natively
# Use a loop script or PM2 instead
```

### Hourly Inbox Triage

**Linux/Mac:**
```cron
# Run at the top of every hour
0 * * * * cd /path/to/AI_employee && python scripts/triage_inbox.py --vault-path /path/to/vault
```

**Windows:**
```powershell
schtasks /create /tn "AIEmployee-Triage" /tr "python C:\path\to\scripts\triage_inbox.py" /sc hourly
```

## Schedule Configuration File

Create `config/schedules.json`:

```json
{
  "schedules": [
    {
      "name": "Daily Briefing",
      "schedule": "0 8 * * *",
      "script": "scripts/daily_briefing.py",
      "enabled": true
    },
    {
      "name": "Weekly Audit",
      "schedule": "0 23 * * 0",
      "script": "scripts/weekly_audit.py",
      "enabled": true
    },
    {
      "name": "Gmail Check",
      "schedule": "*/2 * * * *",
      "script": "scripts/gmail_watcher.py",
      "args": ["--check-once"],
      "enabled": true
    },
    {
      "name": "LinkedIn Post",
      "schedule": "0 9 * * 2,4",
      "script": "scripts/linkedin_post.py",
      "args": ["--queue"],
      "enabled": false
    }
  ]
}
```

Generate crontab from config:

```bash
python scripts/generate_crontab.py --config config/schedules.json --output crontab.txt
```

## Scripted Schedules (Cross-Platform)

For better cross-platform support, use Python schedule library:

```python
# scripts/scheduler.py
import schedule
import time
import subprocess
from pathlib import Path

VAULT_PATH = "/path/to/vault"

def daily_briefing():
    subprocess.run([
        "python", "scripts/daily_briefing.py",
        "--vault-path", VAULT_PATH
    ])

def weekly_audit():
    subprocess.run([
        "python", "scripts/weekly_audit.py",
        "--vault-path", VAULT_PATH
    ])

# Schedule tasks
schedule.every().day.at("08:00").do(daily_briefing)
schedule.every().sunday.at("23:00").do(weekly_audit)
schedule.every(2).minutes.do(check_gmail)

# Run continuously
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run with PM2:

```bash
pm2 start scripts/scheduler.py --interpreter python3 --name ai-scheduler
```

## Cron Quick Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

| Schedule | Cron Expression |
|----------|-----------------|
| Every minute | `* * * * *` |
| Every 5 minutes | `*/5 * * * *` |
| Every hour | `0 * * * *` |
| Every 2 hours | `0 */2 * * *` |
| Daily at 8 AM | `0 8 * * *` |
| Daily at 6 PM | `0 18 * * *` |
| Weekdays at 9 AM | `0 9 * * 1-5` |
| Weekly on Sunday | `0 0 * * 0` |
| Monthly (1st) | `0 0 1 * *` |
| Every 15 minutes | `*/15 * * * *` |

## Environment Variables

Cron runs with minimal environment. Set PATH and variables:

```cron
# At the top of crontab
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/path/to/python
PYTHONPATH=/path/to/AI_employee
VAULT_PATH=/path/to/vault

# Then schedules
0 8 * * * python scripts/daily_briefing.py
```

## Logging Cron Output

```cron
# Log all output
0 8 * * * python scripts/daily_briefing.py >> /path/to/logs/cron.log 2>&1

# Or in config file
{
  "log_path": "/path/to/logs/cron.log",
  "log_level": "INFO"
}
```

## Monitoring Scheduled Tasks

Check if tasks are running:

```bash
# Linux/Mac - view cron logs
grep CRON /var/log/syslog

# View user crontab
crontab -l

# Windows - list tasks
schtasks /query /tn "AIEmployee-*"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cron not running | Check service: `sudo service cron status` |
| Script not found | Use absolute paths in crontab |
| Permission denied | Ensure script is executable: `chmod +x script.py` |
| Python not found | Set PATH in crontab or use full python path |
| No output/logging | Redirect output to log file |
| Task runs multiple times | Check for duplicate crontab entries |

## Best Practices

1. **Use absolute paths** - Avoid relative paths in cron
2. **Log everything** - Redirect stdout/stderr to log files
3. **Use lock files** - Prevent overlapping executions
4. **Set environment** - Define PATH, PYTHONPATH, etc.
5. **Test first** - Run script manually before adding to cron
6. **Use PM2 for frequent tasks** - More reliable than cron for < 5 minute intervals

## Verification

```bash
# Verify crontab syntax
python scripts/verify_crontab.py

# Test a scheduled script
python scripts/daily_briefing.py --dry-run
```

Expected: `✓ Schedule valid, next run at 2026-01-08 08:00:00`
