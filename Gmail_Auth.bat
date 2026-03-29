@echo off
echo ============================================
echo GMAIL AUTHENTICATION - SILVER TIER
echo ============================================
echo.
echo Choose authentication method:
echo.
echo [1] Automatic (recommended)
echo     - Tries multiple ports automatically
echo     - Opens browser automatically
echo.
echo [2] Manual (if automatic fails)
echo     - Shows URL to copy/paste
echo     - You authorize in browser
echo     - Copy code back to this window
echo.
echo [3] Force re-authentication
echo     - Deletes existing token
echo     - Starts fresh
echo.
choice /C 123 /M "Select option"

if errorlevel 3 goto force
if errorlevel 2 goto manual
if errorlevel 1 goto auto

:auto
echo.
echo Running automatic authentication...
cd /d "C:\Users\T14\Documents\GitHub\AI_employee"
python .claude\skills\gmail-watcher\scripts\gmail_auth.py
goto end

:manual
echo.
echo Running manual authentication...
cd /d "C:\Users\T14\Documents\GitHub\AI_employee"
python scripts\gauth_helper.py
goto end

:force
echo.
echo Deleting existing token and re-authenticating...
cd /d "C:\Users\T14\Documents\GitHub\AI_employee"
if exist "config\token.json" del "config\token.json"
echo Token deleted.
echo.
python .claude\skills\gmail-watcher\scripts\gmail_auth.py --force
goto end

:end
echo.
pause
