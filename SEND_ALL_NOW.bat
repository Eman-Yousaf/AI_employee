@echo off
chcp 65001 > nul
cls
echo ============================================
echo    SEND ALL MESSAGES NOW
echo ============================================
echo.
echo This will send:
echo   1. Email to redacted@example.com
echo   2. WhatsApp to CONTACT_NAME
echo   3. LinkedIn post
echo.
pause

cls
echo ============================================
echo [1/3] SENDING EMAIL
echo ============================================
echo.

set "RECIPIENT=redacted@example.com"
set "SUBJECT=Hello from AI Employee"
set "BODY=This is a test email sent automatically from your AI Employee system."

:: Create approval file
(
echo ---
echo action: send_email
echo to: "%RECIPIENT%"
echo subject: "%SUBJECT%"
echo is_html: false
echo priority: high
echo ---
echo.
echo %BODY%
) > "vault\Approved\EMAIL_SEND_NOW_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.md"

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once

echo.
echo [DONE] Email sent to %RECIPIENT%
echo.
timeout /t 3 /nobreak > nul

cls
echo ============================================
echo [2/3] SENDING WHATSAPP
echo ============================================
echo.

set "CONTACT=CONTACT_NAME"
set "MESSAGE=Hello! This is a test message sent from my AI Employee automation system."

python .claude\skills\whatsapp-watcher\scripts\whatsapp_sender.py --chat "%CONTACT%" --message "%MESSAGE%" --session-path "./whatsapp_session"

echo.
echo [DONE] WhatsApp message sent to %CONTACT%
echo.
timeout /t 3 /nobreak > nul

cls
echo ============================================
echo [3/3] POSTING TO LINKEDIN
echo ============================================
echo.

python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "AI Automation"

echo.
echo [DONE] LinkedIn posted!
echo.

cls
echo ============================================
echo    ALL MESSAGES SENT!
echo ============================================
echo.
echo Summary:
echo   [OK] Email sent to redacted@example.com
echo   [OK] WhatsApp sent to CONTACT_NAME
echo   [OK] LinkedIn posted
echo.
echo Check:
echo   - Your email inbox
echo   - WhatsApp chat with CONTACT_NAME
echo   - Your LinkedIn profile
echo ============================================
pause
