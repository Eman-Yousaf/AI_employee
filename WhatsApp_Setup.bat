@echo off
echo ============================================
echo    WHATSAPP SETUP
echo ============================================
echo.
echo This opens WhatsApp Web so you can log in.
echo You only need to do this once!
echo.
echo Steps:
echo 1. Browser will open WhatsApp Web
echo 2. Scan QR code with your phone
echo 3. Close browser when done
echo 4. Session will be saved
echo.
pause

python .claude\skills\whatsapp-watcher\scripts\whatsapp_watcher.py --vault-path vault --show-browser --once

echo.
echo Setup complete! You can now send WhatsApp messages.
pause
