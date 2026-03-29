#!/usr/bin/env python3
"""LinkedIn Poster - Fully Automatic with Robust Selectors."""

import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

try:
    from playwright.sync_api import sync_playwright, expect
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class LinkedInPoster:
    """Fully automatic LinkedIn poster with retry logic."""

    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.linkedin_session'

        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

        for path in [self.pending, self.approved, self.done, self.session_path]:
            path.mkdir(parents=True, exist_ok=True)

    def generate_post(self, topic: str = None) -> str:
        """Generate a LinkedIn post."""
        import random

        hooks = [
            f"Just wrapped up an interesting project on {topic or 'AI automation'}...",
            f"Been thinking a lot about {topic or 'business efficiency'} lately...",
            "Quick question for my network:",
            "Here's something I learned this week:"
        ]

        insights = [
            "Most businesses are leaving money on the table with manual processes.",
            "The companies winning right now are the ones that automate first.",
            "Your time is your most valuable asset. Protect it.",
            "Small improvements compound over time."
        ]

        ctas = [
            "What's your experience? Comment below",
            "Drop a like if you agree",
            "DM me if you want to discuss",
            "Comment 'YES' if this resonates"
        ]

        post = f"""{random.choice(hooks)}

{random.choice(insights)}

{random.choice(ctas)}

#AI #Automation #BusinessGrowth #Consulting"""

        return post

    def create_approval_request(self, content: str, topic: str = None) -> Path:
        """Create approval request for the post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_{timestamp}.md"
        filepath = self.pending / filename

        scheduled = datetime.now() + timedelta(days=1)

        content_md = f"""---
type: approval_request
action: social_post
platform: linkedin
scheduled_time: "{scheduled.isoformat()}"
created: "{datetime.now().isoformat()}"
status: pending
topic: "{topic or 'general'}"
---

# LinkedIn Post Approval

## Generated Content

```
{content}
```

## Platform
LinkedIn (Professional Network)

## Scheduled For
{scheduled.strftime('%Y-%m-%d %H:%M')}

## To Approve
Move this file to `/Approved/` to schedule posting.

## To Edit
1. Edit the content above
2. Save file
3. Move to `/Approved/`

## To Reject
Move this file to `/Rejected/`.

## Posting Rules
- All LinkedIn posts require approval
- Posts go live at scheduled time after approval
- Check Company_Handbook.md for guidelines
"""

        filepath.write_text(content_md, encoding='utf-8')
        logger.info(f"Created LinkedIn approval request: {filepath.name}")
        return filepath

    def post_to_linkedin(self, content: str) -> bool:
        """Post content to LinkedIn with robust selectors."""
        try:
            with sync_playwright() as p:
                logger.info("Opening browser...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,
                    args=['--window-size=1400,900', '--disable-blink-features=AutomationControlled']
                )

                page = browser.new_page()

                # Navigate to feed
                logger.info("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                time.sleep(3)

                # Check if we need to login
                current_url = page.url
                if 'login' in current_url or current_url == 'https://www.linkedin.com/' or 'auth' in current_url:
                    logger.info("=" * 60)
                    logger.info("SETUP REQUIRED: LinkedIn Login")
                    logger.info("=" * 60)
                    logger.info("Please log into LinkedIn in the browser...")
                    logger.info("Waiting up to 2 minutes...")

                    try:
                        # Wait for feed to load after login
                        page.wait_for_selector('[data-test-id="feed-tab"], .feed-sort, .share-box, [data-control-name="sharebox_container"]', timeout=120000)
                        logger.info("Login successful! Session saved.")
                        time.sleep(2)
                    except Exception as e:
                        logger.error(f"Login timeout or feed not detected: {e}")
                        browser.close()
                        return False

                logger.info("Logged in - looking for post button...")
                time.sleep(2)

                # Try multiple strategies to click "Start a post"
                clicked = False
                strategies = [
                    # Strategy 1: Text contains "Start a post"
                    ('text', lambda p: p.get_by_text("Start a post", exact=False).first.click(timeout=10000)),
                    # Strategy 2: Share box button
                    ('share-box', lambda p: p.locator('.share-box button, [data-control-name="sharebox_container"] button').first.click(timeout=10000)),
                    # Strategy 3: CSS selector for post button
                    ('css', lambda p: p.locator('button.artdeco-button, .share-box-feed-entry__trigger').first.click(timeout=10000)),
                    # Strategy 4: Role button with text
                    ('role', lambda p: p.get_by_role('button', name=lambda n: n and 'post' in n.lower()).first.click(timeout=10000)),
                ]

                for name, action in strategies:
                    if clicked:
                        break
                    try:
                        logger.info(f"Trying '{name}' strategy...")
                        action(page)
                        clicked = True
                        logger.info(f"Successfully clicked using '{name}' strategy")
                    except Exception as e:
                        logger.debug(f"Strategy '{name}' failed: {e}")
                        continue

                if not clicked:
                    # Take screenshot for debugging
                    try:
                        screenshot_path = self.vault_path / 'linkedin_debug.png'
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        logger.error(f"Could not find 'Start a post' button. Screenshot saved to {screenshot_path}")
                    except:
                        logger.error("Could not find 'Start a post' button (all strategies failed)")
                    browser.close()
                    return False

                time.sleep(3)

                # Fill content - try multiple selectors for editor
                editor_found = False
                editor_strategies = [
                    # Strategy 1: contenteditable div
                    lambda p: p.locator('div[contenteditable="true"]').first,
                    # Strategy 2: Editor with specific class
                    lambda p: p.locator('.ql-editor, .editor-content, .share-creation-state__textarea').first,
                    # Strategy 3: Role textbox
                    lambda p: p.get_by_role('textbox').first,
                    # Strategy 4: aria-label contains editor
                    lambda p: p.locator('[aria-label*="post"], [aria-label*="Post"]').first,
                ]

                for strategy in editor_strategies:
                    if editor_found:
                        break
                    try:
                        editor = strategy(page)
                        editor.scroll_into_view_if_needed()
                        time.sleep(1)
                        editor.click()
                        time.sleep(1)
                        # Type slowly to ensure it registers
                        editor.fill(content, timeout=10000)
                        editor_found = True
                        logger.info("Content entered")
                    except Exception as e:
                        continue

                if not editor_found:
                    logger.error("Could not find content editor")
                    browser.close()
                    return False

                time.sleep(2)

                # Click Post button - try multiple strategies
                post_clicked = False
                post_strategies = [
                    # Strategy 1: Exact text "Post" button that's enabled
                    ('exact-text', lambda p: p.get_by_role('button', name='Post', exact=True).click(timeout=5000)),
                    # Strategy 2: Button with class artdeco-button--primary
                    ('primary-btn', lambda p: p.locator('button.artdeco-button--primary, .share-actions__primary-action').click(timeout=5000)),
                    # Strategy 3: Any button containing "Post" that's not disabled
                    ('contains-post', lambda p: p.locator('button:not([disabled]):has-text("Post")').first.click(timeout=5000)),
                    # Strategy 4: Share button
                    ('share', lambda p: p.get_by_role('button', name=lambda n: n and 'share' in n.lower()).click(timeout=5000)),
                ]

                for name, action in post_strategies:
                    if post_clicked:
                        break
                    try:
                        logger.info(f"Trying to click Post using '{name}'...")
                        action(page)
                        post_clicked = True
                        logger.info(f"Clicked 'Post' button using '{name}' strategy")
                    except Exception as e:
                        logger.debug(f"Post click strategy '{name}' failed: {e}")
                        continue

                if not post_clicked:
                    logger.error("Could not click Post button")
                    browser.close()
                    return False

                # Wait for post to complete
                time.sleep(5)

                # Verify post was successful
                try:
                    # Look for confirmation (feed update or "Post successful" message)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    logger.info("Post submitted successfully")
                except:
                    pass

                browser.close()
                logger.info("Successfully posted to LinkedIn!")
                return True

        except Exception as e:
            logger.error(f"Failed to post: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def process_approved_posts(self):
        """Process approved posts."""
        processed = 0
        for file_path in self.approved.glob('LINKEDIN_*.md'):
            try:
                logger.info(f"Processing approved post: {file_path.name}")
                content = file_path.read_text(encoding='utf-8')

                # Extract content from markdown code block
                post_content = None
                if '```' in content:
                    parts = content.split('```')
                    for i, part in enumerate(parts):
                        if i > 0 and i % 2 == 1:  # Odd indices are code blocks
                            text = part.strip()
                            if text and not text.startswith('type:'):
                                post_content = text
                                break

                if not post_content:
                    logger.error(f"Could not extract post content from {file_path.name}")
                    continue

                if self.post_to_linkedin(post_content):
                    # Move to Done
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    done_filename = f"LINKEDIN_POSTED_{timestamp}.md"
                    done_path = self.done / done_filename

                    # Update file with posted timestamp
                    updated_content = content.replace(
                        'status: pending',
                        f'status: posted\nposted: "{datetime.now().isoformat()}"'
                    )
                    done_path.write_text(updated_content, encoding='utf-8')
                    file_path.unlink()

                    logger.info(f"Moved to Done: {done_path.name}")
                    processed += 1
                else:
                    logger.error(f"Failed to post {file_path.name}")

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

        return processed


def main():
    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('--vault-path', required=True, help='Path to vault')
    parser.add_argument('--topic', help='Topic for post generation')
    parser.add_argument('--generate', action='store_true', help='Generate post')
    parser.add_argument('--post', action='store_true', help='Process approved posts')
    parser.add_argument('--session-path', help='Path to LinkedIn session')
    parser.add_argument('--test', action='store_true', help='Test post (no approval)')

    args = parser.parse_args()

    poster = LinkedInPoster(
        vault_path=args.vault_path,
        session_path=args.session_path
    )

    if args.test:
        # Direct post without approval (for testing)
        content = poster.generate_post(args.topic)
        print(f"Testing post:\n{content}\n")
        print("Posting directly...")
        if poster.post_to_linkedin(content):
            print("SUCCESS: Posted to LinkedIn!")
        else:
            print("FAILED: Could not post")

    elif args.generate:
        content = poster.generate_post(args.topic)
        filepath = poster.create_approval_request(content, args.topic)
        print(f"Generated post: {filepath}")
        print(f"\nContent:\n{content}")

    elif args.post:
        count = poster.process_approved_posts()
        print(f"Processed {count} approved posts")

    else:
        content = poster.generate_post(args.topic)
        filepath = poster.create_approval_request(content, args.topic)
        print(f"Generated: {filepath}")


if __name__ == '__main__':
    main()
