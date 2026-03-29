@echo off
echo ============================================
echo    AI EMPLOYEE - AUTO PROCESSING
echo ============================================
echo.
echo This runs the automation in the background.
echo Leave this window open and use Obsidian!
echo.
echo What happens automatically:
echo   - Emails in Approved/ get sent
echo   - WhatsApp messages get sent
echo   - LinkedIn posts get published
echo.
pause

:loop
cls
echo ============================================
echo    AUTO PROCESSING - RUNNING
echo ============================================
echo %date% %time% - Checking for new approvals...

python .claude\skills\approval-workflow\scripts\monitor_approved.py --vault-path vault --once

echo.
echo Next check in 60 seconds...
echo Press Ctrl+C to stop
timeout /t 60 /nobreak > nul
goto loop
