@echo off
chcp 65001 > nul
cls
echo ============================================
echo    SEND EMAIL NOW
echo ============================================
echo.

set "RECIPIENT=redacted@example.com"
set "SUBJECT=Hello from AI Employee"
set "BODY=This is a test email sent automatically from your AI Employee system. If you received this, everything is working correctly!"

echo Sending email to: %RECIPIENT%
echo Subject: %SUBJECT%
echo.

:: Create a temp approval file
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

echo File created in Approved folder
echo Executing...
echo.

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once

echo.
echo ============================================
echo Check your email at %RECIPIENT%
echo ============================================
pause
