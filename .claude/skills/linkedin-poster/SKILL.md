---
name: linkedin-poster
description: |
  Automatically generate and post LinkedIn content for business promotion.
  Creates engaging posts from business updates, articles, and sales content.
  Supports scheduling, hashtag optimization, and engagement tracking.
  Use for lead generation, brand awareness, and sales automation.
---

# LinkedIn Poster

Generates and posts business content on LinkedIn to drive sales and engagement.

## Prerequisites

1. LinkedIn account credentials
2. Playwright for browser automation
3. Content templates in vault

## Setup

### 1. Create Content Templates

Create `/Vault/Templates/linkedin_post_template.md`:

```markdown
---
type: linkedin_post_template
purpose: business_promotion
---

## Post Structure

1. Hook (attention-grabbing first line)
2. Value proposition (what's in it for reader)
3. Proof/credibility (results, stats, case study)
4. Call to action (comment, DM, click)
5. Hashtags (3-5 relevant)

## Tone Guidelines
- Professional but conversational
- Use "I" and "you" (personal)
- Short paragraphs (1-2 sentences)
- Emojis sparingly (max 2-3)
```

### 2. Configure Posting Rules

Add to `Company_Handbook.md`:

```markdown
## LinkedIn Posting Rules

### Content Types
- Product updates: Max 1/week
- Industry insights: 2-3/week
- Client testimonials: Max 1/week
- Sales/promotional: Max 1/week

### Posting Times
- Best: Tuesday-Thursday, 8-10 AM or 5-6 PM
- Avoid: Weekends, Monday mornings

### Approval Required
- Any mention of pricing
- Client testimonials (verify permission)
- Competitor comparisons
```

## Usage

### Generate Post

```bash
# Generate post from business update
python scripts/linkedin_generate.py --topic "New AI consulting service" --vault-path /path/to/vault

# Output: Generated post saved to /Pending_Approval/LINKEDIN_2026-01-07.md
```

### Schedule Post

```bash
# Schedule for specific time
python scripts/linkedin_schedule.py --post-file /Pending_Approval/LINKEDIN_2026-01-07.md --schedule "2026-01-08T09:00:00"

# Or use cron
0 9 * * 2-4 python scripts/linkedin_post.py --queue
```

## Content Sources

The poster can generate content from:

1. **Business_Goals.md** - Project milestones
2. **Done/** folder - Completed work
3. **Accounting/** - Revenue milestones (anonymized)
4. **Manual input** - Specific topics

## Output Format

Generated post file:

```markdown
---
type: linkedin_post
status: pending_approval
created: 2026-01-07T10:30:00Z
scheduled: 2026-01-08T09:00:00Z
topic: "AI consulting service launch"
tone: professional
---

## Generated Post

Just helped a client automate 20 hours of weekly manual work using AI.

The result? They reallocated that time to revenue-generating activities.

3 signs your business is ready for AI automation:

1. Repetitive data entry tasks
2. Delayed customer responses
3. Inconsistent follow-ups

If you're seeing these patterns, let's talk.

Comment "AI" below and I'll share my automation checklist.

#AI #Automation #BusinessGrowth #Consulting

---

## To Approve
Move this file to `/Approved/` to schedule posting.

## To Edit
Edit the "Generated Post" section above.

## To Reject
Move this file to `/Rejected/`.
```

## Posting Workflow

1. **Generation**: Claude creates post from business update
2. **Approval**: Human reviews and moves to `/Approved/`
3. **Scheduling**: Orchestrator queues approved posts
4. **Execution**: Playwright posts to LinkedIn at scheduled time
5. **Logging**: Result logged to `/Logs/linkedin_activity.json`

## Safety Controls

### Rate Limiting
- Max 1 post per hour
- Max 5 posts per day
- Cooldown period between posts

### Content Filters
- No profanity
- No competitor bashing
- No unverified claims
- Pricing requires approval

### Human-in-the-Loop
- All posts require approval before publishing
- Emergency stop: Delete from `/Approved/` before post time

## Configuration

Create `config/linkedin_poster.json`:

```json
{
  "vault_path": "/path/to/AI_Employee_Vault",
  "credentials_path": "config/linkedin_credentials.json",
  "max_posts_per_day": 5,
  "posting_window": {
    "start": "08:00",
    "end": "18:00"
  },
  "default_hashtags": ["#AI", "#Automation", "#Business"],
  "content_sources": [
    "Business_Goals.md",
    "Done/",
    "Briefings/"
  ]
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | Check credentials, may need 2FA handling |
| Post rejected | LinkedIn rate limits; reduce frequency |
| Content quality low | Refine templates in Company_Handbook.md |
| Scheduling missed | Verify cron/orchestrator running |

## Security

- Store credentials in keychain/env vars, not in files
- Never commit `linkedin_credentials.json`
- Use dedicated LinkedIn account (not personal)
- Enable 2FA on LinkedIn account

## Verification

```bash
python scripts/verify_linkedin.py
```

Expected: `✓ LinkedIn credentials valid, ready to post`
