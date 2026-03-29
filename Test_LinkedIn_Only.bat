@echo off
chcp 65001 > nul
cls
echo ============================================
echo    TEST LINKEDIN SETUP
echo ============================================
echo.

echo This will test LinkedIn posting.
echo.
echo Choose test type:
echo   1. Quick login test (opens browser, you login)
echo   2. Generate a test post (creates approval file)
echo   3. Post immediately (no approval needed)
echo.
set /p choice="Enter 1, 2, or 3: "

if "%choice%"=="1" (
    echo.
    echo Opening LinkedIn in browser...
    echo Please login if prompted
    echo.
    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "Test"
    echo.
    echo If browser opened and you logged in, setup is complete!
    echo Session will be saved for future use.
)

if "%choice%"=="2" (
    echo.
    echo Generating test post...
    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --generate --topic "AI Automation"
    echo.
    echo Check vault\Pending_Approval\ for the new file
    echo Review it, then move to Approved\ to post
)

if "%choice%"=="3" (
    echo.
    echo This will post immediately to LinkedIn!
    set /p confirm="Are you sure? (yes/no): "
    if /i "%confirm%"=="yes" (
        python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "Testing my new AI automation system"
        echo.
        echo Posted! Check your LinkedIn profile.
    ) else (
        echo Cancelled.
    )
)

echo.
echo ============================================
pause
