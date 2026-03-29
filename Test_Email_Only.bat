@echo off
chcp 65001 > nul
cls
echo ============================================
echo    TEST EMAIL SETUP
echo ============================================
echo.

echo Checking credentials...
if not exist "config\credentials.json" (
    echo [FAIL] credentials.json NOT FOUND
    echo.
    echo You need to:
    echo   1. Go to https://console.cloud.google.com
    echo   2. Create a project
    echo   3. Enable Gmail API
    echo   4. Create OAuth credentials
    echo   5. Download credentials.json
    echo   6. Put in config\ folder
    echo.
    pause
    exit /b 1
)

echo [OK] credentials.json found

echo.
echo Checking authentication...
if not exist "config\token.json" (
    echo [FAIL] Not authenticated
    echo.
    echo Running Gmail_Auth.bat...
    start Gmail_Auth.bat
    echo.
    echo Complete the login in the browser window
    pause
    exit /b 1
)

echo [OK] Already authenticated!

echo.
echo Testing email MCP...
python scripts\mcp_email_client.py --tool tools/list 2>nul
if errorlevel 1 (
    echo [WARN] Could not test MCP (may need dependencies)
    echo.
    echo Install with: pip install google-api-python-client
) else (
    echo [OK] Email MCP responding
)

echo.
echo ============================================
echo Email setup complete!
echo.
echo You can now send emails by:
echo   1. Creating files in vault\Pending_Approval\
echo   2. Moving them to Approved\
echo ============================================
pause
