@echo off
echo ============================================
echo    GENERATE LINKEDIN POST
echo ============================================
echo.
echo This will generate a LinkedIn post
echo and create an approval request.
echo.

set /p topic="Enter topic (or press Enter for general): "

if "%topic%"=="" (
    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --generate
) else (
    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --generate --topic "%topic%"
)

echo.
echo Generated! Check Pending_Approval/ folder in Obsidian.
echo Review and move to Approved/ to post.
pause
