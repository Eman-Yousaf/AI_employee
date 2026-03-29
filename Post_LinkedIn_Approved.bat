@echo off
echo ============================================
echo    POST APPROVED LINKEDIN CONTENT
echo ============================================
echo.
echo This will post all approved LinkedIn content.
echo.
echo Make sure you have:
echo   1. Files in Approved/ folder
echo   2. Logged into LinkedIn before
echo.
pause

python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --post

echo.
echo Done! Check Done/ folder for posted content.
pause
