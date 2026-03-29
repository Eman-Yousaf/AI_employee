@echo off
chcp 65001 > nul
cls
echo ============================================
echo    AI EMPLOYEE - SETUP TESTER
echo ============================================
echo.
echo This will test ALL your setups:
echo   - Gmail/Email
echo   - WhatsApp
echo   - LinkedIn
echo   - Vault Structure
echo.
pause
cls

set "VAULT_PATH=vault"
set "ALL_GOOD=1"

echo ============================================
echo [1/5] TESTING GMAIL SETUP
echo ============================================
echo.

if not exist "config\credentials.json" (
    echo [FAIL] config\credentials.json NOT FOUND
    echo.
    echo To fix:
    echo   1. Get credentials.json from Google Cloud Console
echo   2. Put it in config\ folder
echo   3. Run Gmail_Auth.bat
echo.
    set "ALL_GOOD=0"
) else (
    echo [OK] credentials.json found

    if not exist "config\token.json" (
        echo [FAIL] token.json NOT FOUND
echo.
        echo To fix:
        echo   Run Gmail_Auth.bat to authenticate
echo.
        set "ALL_GOOD=0"
    ) else (
        echo [OK] token.json found - Gmail authenticated!
    )
)

echo.
pause
cls

echo ============================================
echo [2/5] TESTING WHATSAPP SETUP
echo ============================================
echo.

if not exist "whatsapp_session" (
    echo [FAIL] whatsapp_session folder NOT FOUND
    echo.
    echo To fix:
    echo   Run WhatsApp_Setup.bat and scan QR code
echo.
    set "ALL_GOOD=0"
) else (
    dir "whatsapp_session" | findstr "File(s)" > nul
    if errorlevel 1 (
        echo [WARN] whatsapp_session exists but may be empty
        echo [OK] Folder found - session may need refresh
echo.
        echo If WhatsApp fails, run WhatsApp_Setup.bat again
    ) else (
        echo [OK] whatsapp_session found - WhatsApp ready!
    )
)

echo.
pause
cls

echo ============================================
echo [3/5] TESTING LINKEDIN SETUP
echo ============================================
echo.

if not exist "%VAULT_PATH%\.linkedin_session" (
    echo [INFO] LinkedIn session not found
echo.
    echo This is OK - you'll log in on first use.
    echo.
    echo To setup now:
    echo   Run Test_LinkedIn_Post.bat to login and test
echo.
) else (
    echo [OK] LinkedIn session found - LinkedIn ready!
)

echo.
pause
cls

echo ============================================
echo [4/5] TESTING VAULT STRUCTURE
echo ============================================
echo.

echo Checking vault folders...

set "VAULT_OK=1"

if not exist "%VAULT_PATH%\Pending_Approval" (
    echo [FAIL] Pending_Approval/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Pending_Approval/
)

if not exist "%VAULT_PATH%\Approved" (
    echo [FAIL] Approved/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Approved/
)

if not exist "%VAULT_PATH%\Done" (
    echo [FAIL] Done/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Done/
)

if not exist "%VAULT_PATH%\Failed" (
    echo [FAIL] Failed/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Failed/
)

if not exist "%VAULT_PATH%\Needs_Action" (
    echo [FAIL] Needs_Action/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Needs_Action/
)

if not exist "%VAULT_PATH%\Plans" (
    echo [FAIL] Plans/ missing
    set "VAULT_OK=0"
) else (
    echo [OK] Plans/
)

if "%VAULT_OK%"=="0" (
    set "ALL_GOOD=0"
    echo.
    echo [FAIL] Some vault folders missing!
    echo Run Start_Auto_Processing.bat to create them.
)

echo.
pause
cls

echo ============================================
echo [5/5] TESTING PYTHON DEPENDENCIES
echo ============================================
echo.

echo Testing Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found!
    echo.
    echo Install Python from: https://python.org
echo.
    set "ALL_GOOD=0"
) else (
    for /f "tokens=*" %%a in ('python --version 2^>^&1') do echo [OK] %%a
)

echo.
echo Testing Playwright...
python -c "from playwright.sync_api import sync_playwright; print('[OK] Playwright installed')" 2>nul
if errorlevel 1 (
    echo [FAIL] Playwright not installed
    echo.
    echo To fix:
    echo   pip install playwright
echo   playwright install chromium
echo.
    set "ALL_GOOD=0"
) else (
    echo [OK] Playwright installed
)

echo.
echo Testing Google API...
python -c "from google.oauth2.credentials import Credentials; print('[OK] Google API installed')" 2>nul
if errorlevel 1 (
    echo [WARN] Google API not installed (only needed for Gmail API)
    echo.
    echo To fix:
    echo   pip install google-api-python-client
echo.
    echo Or use IMAP version instead (simpler)
) else (
    echo [OK] Google API installed
)

echo.
pause
cls

echo ============================================
echo    TEST COMPLETE
echo ============================================
echo.

if "%ALL_GOOD%"=="1" (
    echo [SUCCESS] All systems ready!
    echo.
    echo You can now:
    echo   1. Run Start_Auto_Processing.bat
echo   2. Use Obsidian to create approvals
echo   3. Everything will work automatically!
echo.
    echo Next steps:
    echo   - Create test email in Pending_Approval/
echo   - Move to Approved/ to test
echo   - Check Done/ for confirmation
) else (
    echo [WARNING] Some issues found!
    echo.
    echo See above for specific fixes.
echo.
    echo Common fixes:
    echo   - Gmail: Run Gmail_Auth.bat
echo   - WhatsApp: Run WhatsApp_Setup.bat
echo   - LinkedIn: Run Test_LinkedIn_Post.bat
echo   - Missing folders: Run Start_Auto_Processing.bat
)

echo.
pause
