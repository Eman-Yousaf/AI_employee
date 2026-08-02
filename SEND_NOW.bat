@echo off
chcp 65001 > nul
cls
echo ============================================
echo    QUICK SEND - TEST HARNESS
echo ============================================
echo.
echo WARNING: this script writes straight into vault\Approved\ and then runs
echo the executor, so it deliberately SKIPS the approval step. Anything sent
echo from here goes out without review. It exists only to confirm that an
echo integration is wired up. Use the Pending_Approval flow for real work.
echo.
echo 1. Send a test email
echo 2. Send a test WhatsApp message
echo 3. Post a test item to LinkedIn
echo.
set /p choice="Enter 1, 2, or 3: "

if "%choice%"=="1" goto email
if "%choice%"=="2" goto whatsapp
if "%choice%"=="3" goto linkedin

echo Invalid choice
goto end

:email
echo.
set /p recipient="Recipient email address: "
if "%recipient%"=="" (echo No recipient given. & goto end)
echo Sending test email to %recipient% ...
(
echo ---
echo action: send_email
echo to: "%recipient%"
echo subject: "Test message from AI Employee"
echo priority: high
echo ---
echo.
echo This is a test email sent from the AI Employee setup harness.
) > "vault\Approved\EMAIL_TEST_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.md"

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once
echo [DONE] Test email dispatched.
goto end

:whatsapp
echo.
set /p contact="WhatsApp contact name (as shown in WhatsApp Web): "
if "%contact%"=="" (echo No contact given. & goto end)
echo Sending test WhatsApp message to %contact% ...
python .claude\skills\whatsapp-watcher\scripts\whatsapp_sender.py --chat "%contact%" --message "Test message from the AI Employee setup harness." --session-path "./whatsapp_session"
echo [DONE] Test WhatsApp message dispatched.
goto end

:linkedin
echo.
set /p topic="Topic for the test post: "
if "%topic%"=="" set topic=AI Automation
echo Generating a test LinkedIn post about "%topic%" ...
python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "%topic%"
echo [DONE] Test LinkedIn post dispatched.
goto end

:end
echo.
pause
