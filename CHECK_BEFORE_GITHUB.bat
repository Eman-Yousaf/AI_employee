@echo off
chcp 65001 > nul
cls
echo ============================================
echo    CHECK BEFORE GITHUB PUSH
necho ============================================
echo.
echo This checks for private files before sharing!
echo.

set "SAFE=1"

echo Checking for private files...
echo.

REM Check credentials
if exist "config\credentials.json" (
    echo [WARNING] config\credentials.json EXISTS
    echo          This should NOT be shared!
    set "SAFE=0"
) else (
    echo [OK] credentials.json not found (good!)
)

if exist "config\token.json" (
    echo [WARNING] config\token.json EXISTS
    echo          This should NOT be shared!
    set "SAFE=0"
) else (
    echo [OK] token.json not found (good!)
)

REM Check .env
if exist ".env" (
    echo [WARNING] .env EXISTS
    echo          This should NOT be shared!
    set "SAFE=0"
) else (
    echo [OK] .env not found (good!)
)

REM Check sessions
if exist "whatsapp_session\*" (
    echo [WARNING] whatsapp_session folder has content
    echo          This should NOT be shared!
    set "SAFE=0"
) else (
    echo [OK] whatsapp_session empty or not found (good!)
)

if exist "vault\.linkedin_session\*" (
    echo [WARNING] vault\.linkedin_session folder has content
    echo          This should NOT be shared!
    set "SAFE=0"
) else (
    echo [OK] .linkedin_session empty or not found (good!)
)

REM Check .gitignore
echo.
echo Checking .gitignore...
if exist ".gitignore" (
    echo [OK] .gitignore exists

    findstr "credentials.json" .gitignore > nul
    if errorlevel 1 (
        echo [WARNING] credentials.json not in .gitignore!
        set "SAFE=0"
    ) else (
        echo [OK] credentials.json is in .gitignore
    )

    findstr "token.json" .gitignore > nul
    if errorlevel 1 (
        echo [WARNING] token.json not in .gitignore!
        set "SAFE=0"
    ) else (
        echo [OK] token.json is in .gitignore
    )

    findstr "whatsapp_session" .gitignore > nul
    if errorlevel 1 (
        echo [WARNING] whatsapp_session not in .gitignore!
        set "SAFE=0"
    ) else (
        echo [OK] whatsapp_session is in .gitignore
    )
) else (
    echo [ERROR] .gitignore NOT FOUND!
    echo        Creating one now...
    echo [WARNING] Please review GITHUB_GUIDE.md
    set "SAFE=0"
)

echo.
echo ============================================

if "%SAFE%"=="1" (
    echo [SUCCESS] Ready to push to GitHub!
    echo.
    echo Your private data is protected.
    echo Run: git push origin main
) else (
    echo [WARNING] Issues found! See above.
    echo.
    echo Read GITHUB_GUIDE.md to fix these issues.
    echo.
    echo Quick fixes:
    echo   1. Delete private files (keep backups!)
    echo   2. Check .gitignore is complete
    echo   3. Run git status to verify
)

echo ============================================
pause
