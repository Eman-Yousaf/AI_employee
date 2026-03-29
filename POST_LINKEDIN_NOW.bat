@echo off
chcp 65001 > nul
cls
echo ============================================
echo    POST TO LINKEDIN NOW
echo ============================================
echo.
echo This will post immediately to your LinkedIn profile!
echo.

set "POST_CONTENT=Excited to share that I've implemented an AI automation system to handle my business communications!

This system now manages emails, WhatsApp messages, and LinkedIn posts - saving hours every week.

The future of business is automation. Are you ready?

#AI #Automation #BusinessEfficiency #Innovation"

echo Your post will be:
echo --------------------------------------------------
echo %POST_CONTENT%
echo --------------------------------------------------
echo.

set /p confirm="Post this now? (yes/no): "

if /i "%confirm%"=="yes" (
    cls
    echo Posting to LinkedIn...
    echo Browser will open...
    echo.

    python .claude\skills\linkedin-poster\scripts\linkedin_poster.py --vault-path vault --test --topic "AI Automation"

    echo.
    echo ============================================
    echo Check your LinkedIn profile!
    echo ============================================
) else (
    echo Cancelled.
)

pause
