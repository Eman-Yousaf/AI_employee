# Quick Start Templates

## How to Use These Templates

1. **Copy** any template file
2. **Paste** it into `Pending_Approval/` folder
3. **Fill in** the empty fields
4. **Move** to `Approved/` when ready to send

---

## Template 1: Email to Client

**File:** `email_client_template.md`

Copy this template, fill in the blanks, save to `Pending_Approval/`

```markdown
---
action: send_email
to: "CLIENT_EMAIL_HERE"
subject: "SUBJECT_HERE"
priority: medium
---

Dear [Name],

[Your message here]

Best regards,
[Your name]
```

---

## Template 2: WhatsApp Message

**File:** `whatsapp_template.md`

```markdown
---
action: send_whatsapp
chat_name: "CONTACT_NAME"
priority: medium
---

Hi [Name],

[Your message here]
```

---

## Template 3: LinkedIn Post

**File:** `linkedin_template.md`

```markdown
---
action: social_post
platform: linkedin
---

[Your LinkedIn post content]

#hashtag1 #hashtag2
```

---

## Ready-Made Examples

### Example: Follow-up Email

Copy this exactly (just change the email address):

```markdown
---
action: send_email
to: "client@example.com"
subject: "Following up on our meeting"
priority: medium
---

Hi,

I wanted to follow up on our meeting yesterday. As discussed, I'll send over the proposal by end of week.

Let me know if you have any questions.

Best regards
```

### Example: WhatsApp Quick Message

```markdown
---
action: send_whatsapp
chat_name: "John Smith"
priority: high
---

Hi John, quick reminder about the call in 30 minutes.
```

### Example: LinkedIn Business Update

```markdown
---
action: social_post
platform: linkedin
---

Excited to announce we've just completed a major milestone in our AI automation project!

The new system is now handling 1000+ tasks daily with zero manual intervention.

#AI #Automation #BusinessGrowth #Innovation
```

---

## Step-by-Step for Beginners

### To Send an Email:

1. Click on `Pending_Approval/` folder
2. Click "New Note" (or press Ctrl+N)
3. Name it: `email_[purpose]`
4. Copy the email template above
5. Fill in:
   - `to:` the email address
   - `subject:` what the email is about
   - Body: the actual message
6. Save (Ctrl+S)
7. Drag the file to `Approved/` folder
8. Done! The system will send it automatically

### To Send WhatsApp:

1. Create new note in `Pending_Approval/`
2. Copy WhatsApp template
3. Fill in:
   - `chat_name:` exact contact name as in WhatsApp
   - Body: the message
4. Save
5. Drag to `Approved/`

### To Check What Happened:

- **Sent successfully?** → Check `Done/` folder
- **Failed?** → Check `Failed/` folder
- **Details?** → Check `Logs/executed_approvals.json`

---

## Common Mistakes to Avoid

1. ❌ Don't put files directly in `Approved/` - always review first in `Pending_Approval/`
2. ❌ Don't forget the `---` before and after the frontmatter
3. ❌ Don't use special characters in chat names
4. ❌ Don't forget quotes around email addresses
5. ✅ Always check `Done/` to confirm it worked

---

## Practice Exercise

Try this test:

1. Create a file in `Pending_Approval/test_email.md`
2. Paste this:

```markdown
---
action: send_email
to: "your-own-email@example.com"
subject: "Test message"
priority: low
---

This is a test email from my AI Employee system.

If you received this, everything is working!
```

3. Move it to `Approved/`
4. Check your email in a few minutes
5. Check `Done/` folder - the file should be there

Congratulations! You just sent your first automated email!
