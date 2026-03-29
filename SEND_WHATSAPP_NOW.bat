@echo off
chcp 65001 > nul
cls
echo ============================================
echo    SEND WHATSAPP NOW
echo ============================================
echo.

set "CONTACT=CONTACT_NAME"
set "MESSAGE=Hello! This is a test message sent from my AI Employee automation system."

echo Sending WhatsApp message to: %CONTACT%
echo Message: %MESSAGE%
echo.
echo Make sure WhatsApp Web is logged in!
echo.
pause

cls
echo Opening WhatsApp and sending message...
echo This may take 10-20 seconds...
echo.

python .claude\skills\whatsapp-watcher\scripts\whatsapp_sender.py --chat "%CONTACT%" --message "%MESSAGE%" --session-path "./whatsapp_session"

echo.
echo ============================================
if %errorlevel% == 0 (
    echo [SUCCESS] Message sent to %CONTACT%!
) else (
    echo [ERROR] Failed to send. Check if logged in.
)
echo ============================================
pause
