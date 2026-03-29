---
name: reasoning-loop
description: |
  Ralph Wiggum persistence pattern for autonomous multi-step task completion.
  Keeps Claude working on tasks until complete by intercepting exit attempts.
  Uses completion promises and file-based state tracking.
  Use for complex workflows requiring multiple steps and persistent execution.
---

# Reasoning Loop (Ralph Wiggum Pattern)

Persistent execution pattern that keeps Claude working until tasks are complete.

## Overview

Claude Code normally exits after each prompt. The Reasoning Loop ("Ralph Wiggum" pattern) keeps Claude iterating until a task is fully complete.

```
Traditional: Prompt → Claude works → Exit → User prompts again
Ralph Loop: Prompt → Claude works → Detect incomplete → Re-prompt → Continue...
```

## How It Works

1. **Start Loop** - Begin with task description
2. **Claude Works** - Processes one or more steps
3. **Check Completion** - Is the task done?
4. **Continue or Exit** - If not done, loop back with context

## Implementation

### Method 1: Stop Hook (Recommended)

Configure in Claude Code settings:

```json
// ~/.config/claude-code/settings.json
{
  "hooks": {
    "Stop": {
      "command": "python scripts/ralph_hook.py",
      "args": ["--vault-path", "/path/to/vault"]
    }
  }
}
```

`scripts/ralph_hook.py`:

```python
#!/usr/bin/env python3
"""Ralph Wiggum Stop Hook - prevents exit if work incomplete."""

import sys
import json
from pathlib import Path

def check_completion():
    """Check if current task is complete."""
    vault_path = Path(sys.argv[sys.argv.index("--vault-path") + 1])

    # Check for active plans with incomplete steps
    plans_path = vault_path / "Plans"
    for plan_file in plans_path.glob("PLAN_*.md"):
        content = plan_file.read_text()

        # Check for unchecked items
        if "- [ ]" in content or "- [-]" in content:
            return False, f"Plan has incomplete steps: {plan_file.name}"

    # Check for items in Needs_Action
    needs_action = vault_path / "Needs_Action"
    if any(needs_action.iterdir()):
        return False, "Items pending in Needs_Action"

    return True, "All tasks complete"

def main():
    is_complete, reason = check_completion()

    if not is_complete:
        # Block exit and provide continuation prompt
        result = {
            "continue": True,
            "prompt": f"Task incomplete: {reason}. Continue working. Check Plans/ for current status.",
            "context": {
                "reason": reason,
                "next_action": "Continue from where you left off"
            }
        }
        print(json.dumps(result))
        sys.exit(1)  # Block exit
    else:
        # Allow exit
        print(json.dumps({"continue": False}))
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### Method 2: Promise-Based

Claude outputs a completion promise when done:

```python
# In Claude prompt, instruct to output promise when complete
"""
Work on the task. When complete, output: <promise>TASK_COMPLETE</promise>
"""
```

Hook checks for promise:

```python
def check_completion():
    # Read Claude's last output from context
    last_output = get_last_claude_output()

    if "<promise>TASK_COMPLETE</promise>" in last_output:
        return True, "Task complete promise found"

    return False, "No completion promise found"
```

### Method 3: File-Based State

Track task state in files:

```python
# scripts/start_task.py
def start_task(task_description):
    task_id = generate_task_id()
    task_file = Path("Tasks") / f"TASK_{task_id}.json"

    task_file.write_text(json.dumps({
        "id": task_id,
        "description": task_description,
        "status": "active",
        "started": datetime.now().isoformat(),
        "plan": None,
        "completed_steps": [],
        "remaining_steps": []
    }))

    return task_id
```

Hook checks task file:

```python
def check_completion():
    tasks = Path("Tasks").glob("TASK_*.json")
    active_tasks = [t for t in tasks if json.loads(t.read_text())["status"] == "active"]

    if active_tasks:
        task = json.loads(active_tasks[0].read_text())
        return False, f"Active task: {task['description']}"

    return True, "No active tasks"
```

## Usage

### Start a Ralph Loop

```bash
# CLI command (custom implementation)
claude-loop "Process all files in /Needs_Action and create plans for each"

# Or via settings.json hook (automatic)
claude "Process all items in Needs_Action"
# When Claude tries to exit, hook intercepts and continues if incomplete
```

### Stop a Ralph Loop

```bash
# Create completion marker
echo "TASK_COMPLETE" > /tmp/completion_marker

# Or move all plans to Done
mv Plans/PLAN_* Done/

# Or use signal
claude-loop --stop
```

## Integration with Plans

The Ralph Loop works seamlessly with the Plan Creator:

```markdown
# Plan Example

## Steps
- [x] Step 1: Analyze request
- [x] Step 2: Gather information
- [-] Step 3: Draft response
- [ ] Step 4: Review and send
```

Ralph Loop sees `[-]` (in progress) and ` [ ]` (not started) → Continues

When all `[x]` → Allows exit

## Max Iterations

Prevent infinite loops:

```python
# Add iteration counter to task state
def check_completion():
    state = load_state()
    state["iterations"] = state.get("iterations", 0) + 1

    if state["iterations"] > 10:
        save_state(state)
        return True, "Max iterations reached - forcing exit"

    save_state(state)
    # ... normal completion check
```

## Error Handling

Handle failures gracefully:

```python
def check_completion():
    try:
        # ... completion checks
    except Exception as e:
        # Log error and allow exit to prevent lockup
        log_error(f"Ralph hook error: {e}")
        return True, f"Error in hook: {e}"
```

## Configuration

Create `config/reasoning_loop.json`:

```json
{
  "mode": "file_based",
  "max_iterations": 10,
  "check_interval": "on_exit",
  "completion_indicators": {
    "plans_complete": true,
    "needs_action_empty": true,
    "pending_approval_empty": false
  },
  "continue_prompt": "Continue working on the active task. Check Plans/ for current status."
}
```

## Debugging

```bash
# Test hook manually
python scripts/ralph_hook.py --vault-path /path/to/vault --debug

# Expected output when incomplete:
# {"continue": true, "prompt": "Task incomplete..."}

# Expected output when complete:
# {"continue": false}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Infinite loop | Check max_iterations, verify completion criteria |
| Hook not firing | Verify settings.json hook configuration |
| Claude confused | Provide clear context in continue_prompt |
| Performance issues | Reduce check frequency, optimize file checks |
| Stuck on task | Manually move plan to Done/ or create completion marker |

## Best Practices

1. **Set max iterations** - Always prevent infinite loops
2. **Log decisions** - Track why loop continued or exited
3. **Clear completion criteria** - Define exactly what "done" means
4. **Save progress** - Write state frequently in case of interruption
5. **Human override** - Provide way to force exit if needed
6. **Test hook independently** - Verify hook logic before using

## Reference

Original Ralph Wiggum pattern: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
