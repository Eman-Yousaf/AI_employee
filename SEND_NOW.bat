@echo off
chcp 65001 > nul
cls
echo ============================================
echo    QUICK SEND - CHOOSE OPTION
echo ============================================
echo.
echo 1. Send Email to redacted@example.com
echo 2. Send WhatsApp to CONTACT_NAME
echo 3. Post to LinkedIn
echo 4. Send ALL at once
echo.
set /p choice="Enter 1, 2, 3, or 4: "

if "%choice%"=="1" goto email
if "%choice%"=="2" goto whatsapp
if "%choice%"=="3" goto linkedin
if "%choice%"=="4" goto all

echo Invalid choice
goto end

:email
echo.
echo Sending email...
(
echo ---
echo action: send_email
echo to: "redacted@example.com"
echo subject: "Hello from AI Employee"
echo priority: high
echo ---
echo.
echo This is a test email sent automatically from your AI Employee system.
) > "vault\Approved\EMAIL_NOW_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.md"

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once
echo [DONE] Email sent!
goto end

:whatsapp
echo.
echo Sending WhatsApp...
python .claude\skills\whatsapp-watcher\scripts\whatsapp_sender.py --chat "CONTACT_NAME" --message "Hello! This is a test message from AI Employee system." --session-path "./whatsapp_session"
echo [DONE] WhatsApp sent!
goto end

:linkedin
echo.
echo Posting to LinkedIn...
python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "AI Automation"
echo [DONE] LinkedIn posted!
goto end

:all
echo.
echo Sending Email...
(
echo ---
echo action: send_email
echo to: "redacted@example.com"
echo subject: "Hello from AI Employee"
echo priority: high
echo ---
echo.
echo This is a test email sent automatically from your AI Employee system.
) > "vault\Approved\EMAIL_NOW_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.md"
python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once
echo [DONE] Email sent!
echo.

echo Sending WhatsApp...
python .claude\skills\whatsapp-watcher\scripts\whatsapp_sender.py --chat "CONTACT_NAME" --message "Hello! This is a test message from AI Employee system." --session-path "./whatsapp_session"
echo [DONE] WhatsApp sent!
echo.

echo Posting to LinkedIn...
python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "AI Automation"
echo [DONE] LinkedIn posted!
echo.

echo ============================================
echo ALL MESSAGES SENT!
echo ============================================

:end
echo.
pause
