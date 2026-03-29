#!/usr/bin/env python3
"""Scheduler - Python-based scheduler for recurring tasks."""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Callable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Cross-platform task scheduler."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tasks: List[Dict] = []
        self.running = False

        logger.info(f"TaskScheduler initialized")

    def add_task(self, name: str, schedule: str, command: List[str]):
        """Add a task to the scheduler."""
        self.tasks.append({
            'name': name,
            'schedule': schedule,  # cron-style or special keywords
            'command': command,
            'last_run': None
        })
        logger.info(f"Added task: {name}")

    def should_run(self, task: Dict) -> bool:
        """Check if a task should run now."""
        now = datetime.now()
        schedule = task['schedule']

        # Parse schedule
        if schedule == 'daily_8am':
            return now.hour == 8 and now.minute == 0
        elif schedule == 'weekly_sunday_11pm':
            return now.weekday() == 6 and now.hour == 23 and now.minute == 0
        elif schedule == 'hourly':
            return now.minute == 0
        elif schedule == 'every_2_minutes':
            return now.minute % 2 == 0
        elif schedule.startswith('custom:'):
            # Parse cron-like: minute hour day month weekday
            parts = schedule.replace('custom:', '').split()
            if len(parts) == 5:
                minute, hour, day, month, weekday = parts
                if minute != '*' and int(minute) != now.minute:
                    return False
                if hour != '*' and int(hour) != now.hour:
                    return False
                if weekday != '*' and int(weekday) != now.weekday():
                    return False
                return True

        return False

    def run_task(self, task: Dict):
        """Execute a task."""
        logger.info(f"Running task: {task['name']}")

        try:
            result = subprocess.run(
                task['command'],
                capture_output=True,
                text=True,
                cwd=str(self.vault_path.parent)
            )

            if result.returncode == 0:
                logger.info(f"Task {task['name']} completed successfully")
            else:
                logger.error(f"Task {task['name']} failed: {result.stderr}")

            task['last_run'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error running task {task['name']}: {e}")

    def run(self):
        """Run the scheduler loop."""
        self.running = True
        logger.info("Scheduler started")

        while self.running:
            now = datetime.now()

            for task in self.tasks:
                if self.should_run(task):
                    # Check if already ran this minute
                    if task['last_run']:
                        last = datetime.fromisoformat(task['last_run'])
                        if last.minute == now.minute and last.hour == now.hour:
                            continue

                    self.run_task(task)

            # Sleep until next minute
            time.sleep(60 - now.second)

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        logger.info("Scheduler stopping...")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Task Scheduler')
    parser.add_argument('--vault-path', required=True, help='Path to vault')
    parser.add_argument('--config', help='Path to schedule config JSON')

    args = parser.parse_args()

    scheduler = TaskScheduler(vault_path=args.vault_path)

    # Load config or use defaults
    if args.config and Path(args.config).exists():
        config = json.loads(Path(args.config).read_text())
        for task in config.get('tasks', []):
            scheduler.add_task(
                name=task['name'],
                schedule=task['schedule'],
                command=task['command']
            )
    else:
        # Default tasks
        scheduler.add_task(
            name='daily_briefing',
            schedule='daily_8am',
            command=['python', 'scripts/daily_briefing.py', '--vault-path', args.vault_path]
        )
        scheduler.add_task(
            name='weekly_audit',
            schedule='weekly_sunday_11pm',
            command=['python', 'scripts/weekly_audit.py', '--vault-path', args.vault_path]
        )

    try:
        scheduler.run()
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == '__main__':
    main()
