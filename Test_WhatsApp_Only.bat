@echo off
chcp 65001 > nul
cls
echo ============================================
echo    TEST WHATSAPP SETUP
echo ============================================
echo.

echo Checking WhatsApp session...
if not exist "whatsapp_session" (
    echo [FAIL] WhatsApp not set up yet
    echo.
    echo Setting up now...
    echo.
    python .claude\skills\whatsapp-watcher\scripts\whatsapp_watcher.py --vault-path vault --show-browser --once
    echo.
    echo If browser opened, scan QR code with your phone
    pause
    exit /b 1
)

echo [OK] WhatsApp session found!
echo.
echo Testing by checking for messages...
python .claude\skills\whatsapp-watcher\scripts\whatsapp_watcher.py --vault-path vault --once

echo.
if exist "vault\Needs_Action\WHATSAPP_*.md" (
    echo [SUCCESS] WhatsApp is working!
    echo Found new messages in Needs_Action/
) else (
    echo [OK] WhatsApp configured
    echo No new messages found (this is normal)
)

echo.
echo ============================================
echo WhatsApp setup complete!
echo.
echo You can now send WhatsApp messages by:
echo   1. Creating files in vault\Pending_Approval\
echo   2. Moving them to Approved\
echo ============================================
pause
