@echo off
echo ============================================
echo    CHECK GMAIL (IMAP VERSION)
echo ============================================
echo.
echo This uses IMAP (simpler than Gmail API).
echo.
echo Before running:
echo 1. Read SIMPLE_EMAIL_SETUP.md
echo 2. Create .env file with your email and app password
echo.
pause

python .claude\skills\gmail-watcher\scripts\gmail_imap.py --vault-path vault

echo.
echo Done! Check vault\Needs_Action folder for new emails.
pause
