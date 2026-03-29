@echo off
echo ============================================
echo    TEST LINKEDIN POSTING
echo ============================================
echo.
echo This will test LinkedIn posting WITHOUT approval.
echo It posts immediately!
echo.
echo Use this to:
echo   - Test if LinkedIn login works
echo   - See how posting works
echo.
set /p confirm="Are you sure? (yes/no): "

if /i "%confirm%"=="yes" (
    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "AI Automation"
    echo.
    echo Test complete!
) else (
    echo Cancelled.
)

pause
