# PowerShell script to configure Google Cloud credentials for Olist Dashboard

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Olist Dashboard - PowerShell Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Get the current directory (where the script is located)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CredentialsFile = Join-Path $ScriptDir "project-olist-470307-credentials.json"

Write-Host ""
Write-Host "Current directory: $ScriptDir" -ForegroundColor Yellow
Write-Host "Credentials file: $CredentialsFile" -ForegroundColor Yellow

# Check if credentials file exists
if (-not (Test-Path $CredentialsFile)) {
    Write-Host "ERROR: Credentials file not found!" -ForegroundColor Red
    Write-Host "Please ensure project-olist-470307-credentials.json is in the project directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Credentials file found!" -ForegroundColor Green

# Option 1: Set environment variable for current session
Write-Host ""
Write-Host "Setting GOOGLE_APPLICATION_CREDENTIALS for current session..." -ForegroundColor Yellow
$env:GOOGLE_APPLICATION_CREDENTIALS = $CredentialsFile
Write-Host "✓ Environment variable set for current session" -ForegroundColor Green

# Option 2: Set permanent environment variable
Write-Host ""
Write-Host "Setting permanent environment variable..." -ForegroundColor Yellow
try {
    [Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", $CredentialsFile, "User")
    Write-Host "✓ Permanent environment variable set successfully" -ForegroundColor Green
    Write-Host "  (Changes will take effect in new PowerShell sessions)" -ForegroundColor Gray
} catch {
    Write-Host "⚠ Could not set permanent environment variable" -ForegroundColor Yellow
    Write-Host "  (May require administrator privileges)" -ForegroundColor Yellow
    Write-Host "  Using session-only variable instead" -ForegroundColor Yellow
}

# Verify setup
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GOOGLE_APPLICATION_CREDENTIALS = $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor White

# Test Google Cloud authentication
Write-Host ""
Write-Host "Testing Google Cloud authentication..." -ForegroundColor Yellow
try {
    # Try to import the Google Cloud BigQuery module (if available)
    python -c "
from google.cloud import bigquery
from google.oauth2 import service_account
import os

creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if creds_path and os.path.exists(creds_path):
    credentials = service_account.Credentials.from_service_account_file(creds_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    print(f'✓ Successfully authenticated with project: {credentials.project_id}')
else:
    print('⚠ Credentials file not found in environment variable')
" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Google Cloud authentication test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Google Cloud libraries may not be installed yet" -ForegroundColor Yellow
        Write-Host "  Install dependencies first: pip install -r requirements.txt" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ Could not test authentication (Python/dependencies may not be installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Activate your conda environment: conda activate olist-dashboard" -ForegroundColor Gray
Write-Host "2. Install dependencies (if not done): pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "3. Run the Streamlit app: streamlit run main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Alternative authentication methods:" -ForegroundColor White
Write-Host "- The app will also try to use .streamlit/secrets.toml (already configured)" -ForegroundColor Gray
Write-Host "- Or the relative path to project-olist-470307-credentials.json" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
