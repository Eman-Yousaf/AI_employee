#!/usr/bin/env python3
"""Ralph Wiggum Stop Hook - Prevents Claude exit if work incomplete."""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RalphHook:
    """Ralph Wiggum persistence hook."""

    def __init__(self, vault_path: str, max_iterations: int = 10):
        self.vault_path = Path(vault_path)
        self.plans = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'

        self.max_iterations = max_iterations
        self.iteration_file = self.vault_path / '.ralph_iterations.json'

        logger.info(f"RalphHook initialized")

    def get_iteration_count(self) -> int:
        """Get current iteration count."""
        if self.iteration_file.exists():
            try:
                data = json.loads(self.iteration_file.read_text())
                return data.get('count', 0)
            except:
                pass
        return 0

    def increment_iteration(self):
        """Increment iteration count."""
        count = self.get_iteration_count() + 1
        self.iteration_file.write_text(json.dumps({
            'count': count,
            'last_update': datetime.now().isoformat()
        }))
        return count

    def reset_iterations(self):
        """Reset iteration counter."""
        if self.iteration_file.exists():
            self.iteration_file.unlink()

    def check_active_plans(self) -> Tuple[bool, str]:
        """Check for active plans with incomplete steps."""
        if not self.plans.exists():
            return False, "No plans directory"

        for plan_file in self.plans.glob('PLAN_*.md'):
            try:
                content = plan_file.read_text()

                # Check for incomplete steps
                # [ ] = not started, [-] = in progress
                if '- [ ]' in content or '- [-]' in content:
                    # Count completed vs total
                    total = content.count('- [ ]') + content.count('- [-]') + content.count('- [x]')
                    completed = content.count('- [x]')

                    return True, f"Plan {plan_file.name}: {completed}/{total} steps complete"

            except Exception as e:
                logger.error(f"Error reading {plan_file}: {e}")

        return False, "All plans complete"

    def check_needs_action(self) -> Tuple[bool, str]:
        """Check for items in Needs_Action."""
        if not self.needs_action.exists():
            return False, "No needs action directory"

        count = len(list(self.needs_action.glob('*.md')))
        if count > 0:
            return True, f"{count} items pending in Needs_Action"

        return False, "No items in Needs_Action"

    def check_in_progress(self) -> Tuple[bool, str]:
        """Check for items in In_Progress."""
        if not self.in_progress.exists():
            return False, "No in progress directory"

        count = len(list(self.in_progress.glob('*.md')))
        if count > 0:
            return True, f"{count} items in In_Progress"

        return False, "No items in In_Progress"

    def check_completion(self) -> Tuple[bool, str]:
        """Check if all work is complete."""
        # Check iteration limit
        iteration = self.get_iteration_count()
        if iteration >= self.max_iterations:
            self.reset_iterations()
            return True, f"Max iterations ({self.max_iterations}) reached - forcing exit"

        # Check various completion criteria
        checks = [
            self.check_active_plans(),
            self.check_needs_action(),
            self.check_in_progress()
        ]

        incomplete = [c for c in checks if c[0]]

        if incomplete:
            reasons = '; '.join([c[1] for c in incomplete])
            return False, reasons

        # All checks passed
        self.reset_iterations()
        return True, "All tasks complete"

    def get_context(self) -> str:
        """Get context for continuation prompt."""
        context_parts = []

        # List active plans
        if self.plans.exists():
            active_plans = []
            for plan_file in self.plans.glob('PLAN_*.md'):
                try:
                    content = plan_file.read_text()
                    total = content.count('- [ ]') + content.count('- [-]') + content.count('- [x]')
                    completed = content.count('- [x]')
                    if total > 0:
                        active_plans.append(f"{plan_file.name} ({completed}/{total})")
                except:
                    pass

            if active_plans:
                context_parts.append(f"Active plans: {', '.join(active_plans)}")

        # Count pending items
        needs_action_count = len(list(self.needs_action.glob('*.md'))) if self.needs_action.exists() else 0
        if needs_action_count > 0:
            context_parts.append(f"Needs_Action: {needs_action_count} items")

        return '; '.join(context_parts) if context_parts else "Check vault folders for status"

    def handle_stop(self) -> Dict:
        """Handle Stop hook event."""
        try:
            is_complete, reason = self.check_completion()

            if not is_complete:
                iteration = self.increment_iteration()
                context = self.get_context()

                result = {
                    "continue": True,
                    "prompt": f"Task incomplete ({reason}). Continue working. Iteration {iteration}/{self.max_iterations}. Context: {context}",
                    "context": {
                        "reason": reason,
                        "iteration": iteration,
                        "max_iterations": self.max_iterations,
                        "vault_status": context
                    }
                }

                logger.info(f"Blocking exit: {reason}")
                return result
            else:
                self.reset_iterations()
                logger.info(f"Allowing exit: {reason}")
                return {"continue": False}

        except Exception as e:
            logger.error(f"Error in Ralph hook: {e}")
            # On error, allow exit to prevent lockup
            return {"continue": False, "error": str(e)}


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Hook')
    parser.add_argument('--vault-path', default='./vault', help='Path to vault')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max iterations')

    args = parser.parse_args()

    hook = RalphHook(
        vault_path=args.vault_path,
        max_iterations=args.max_iterations
    )

    result = hook.handle_stop()
    print(json.dumps(result))

    # Exit with appropriate code
    sys.exit(0 if not result.get('continue') else 1)


if __name__ == '__main__':
    main()
