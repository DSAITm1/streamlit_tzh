@echo off
REM Windows batch script to configure Google Cloud credentials for Olist Dashboard

echo ========================================
echo Olist Dashboard - Windows Setup Script
echo ========================================

REM Get the current directory (where the script is located)
set SCRIPT_DIR=%~dp0
set CREDENTIALS_FILE=%SCRIPT_DIR%project-olist-470307-credentials.json

echo.
echo Current directory: %SCRIPT_DIR%
echo Credentials file: %CREDENTIALS_FILE%

REM Check if credentials file exists
if not exist "%CREDENTIALS_FILE%" (
    echo ERROR: Credentials file not found!
    echo Please ensure project-olist-470307-credentials.json is in the project directory.
    pause
    exit /b 1
)

echo ✓ Credentials file found!

REM Option 1: Set environment variable for current session
echo.
echo Setting GOOGLE_APPLICATION_CREDENTIALS for current session...
set GOOGLE_APPLICATION_CREDENTIALS=%CREDENTIALS_FILE%
echo ✓ Environment variable set for current session

REM Option 2: Set permanent environment variable (requires admin)
echo.
echo Setting permanent environment variable...
setx GOOGLE_APPLICATION_CREDENTIALS "%CREDENTIALS_FILE%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Permanent environment variable set successfully
    echo   ^(Changes will take effect in new command prompt sessions^)
) else (
    echo ⚠ Could not set permanent environment variable
    echo   ^(May require administrator privileges^)
    echo   Using session-only variable instead
)

REM Verify setup
echo.
echo ========================================
echo Verification
echo ========================================
echo GOOGLE_APPLICATION_CREDENTIALS = %GOOGLE_APPLICATION_CREDENTIALS%

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate your conda environment: conda activate olist-dashboard
echo 2. Run the Streamlit app: streamlit run main.py
echo.
echo Note: If you opened a new command prompt, the permanent environment
echo       variable should be available. Otherwise, run this script again.
echo.

pause
