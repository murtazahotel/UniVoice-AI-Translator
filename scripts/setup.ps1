# Setup script for UniVoice development environment (Windows)

Write-Host "Setting up UniVoice development environment..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+' | ForEach-Object { $_.Matches.Value }
$requiredVersion = [version]"3.11.0"

if ([version]$pythonVersion -lt $requiredVersion) {
    Write-Host "Error: Python 3.11 or higher is required" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Copy environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..."
    Copy-Item .env.example .env
    Write-Host "✓ .env file created (please update with your configuration)" -ForegroundColor Green
}

# Create necessary directories
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Activate the virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Update .env file with your AWS credentials and configuration"
Write-Host "3. Run tests: pytest"
Write-Host "4. Start services: docker-compose up"
