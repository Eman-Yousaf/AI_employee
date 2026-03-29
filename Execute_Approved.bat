@echo off
echo ============================================
echo    EXECUTE APPROVED ITEMS
echo ============================================
echo.
echo This processes all files in Approved/ folder.
echo.
echo Sending:
echo   - Emails via Gmail
echo   - WhatsApp messages
echo   - LinkedIn posts
echo.

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once

echo.
echo Done! Check Done/ folder for completed items.
echo Check Failed/ folder for any errors.
pause
