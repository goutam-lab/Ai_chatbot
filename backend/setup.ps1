# Setup script for the backend

# Get the script's directory
$scriptPath = $PSScriptRoot
Set-Location $scriptPath

# Check if MongoDB service is running
try {
    $mongoService = Get-Service -Name "MongoDB" -ErrorAction Stop
    if ($mongoService.Status -ne "Running") {
        Write-Host "Starting MongoDB service..."
        Start-Service -Name "MongoDB"
        Start-Sleep -Seconds 5  # Wait for service to start
    }
    Write-Host "MongoDB service is running"
} catch {
    Write-Host "MongoDB service not found. Please install MongoDB and ensure the service is running."
    Write-Host "You can download MongoDB from: https://www.mongodb.com/try/download/community"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    @"
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=your_assistant_id_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=zomato_db
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Please update the .env file with your actual API keys and MongoDB connection details"
}

# Add the current directory to PYTHONPATH
$env:PYTHONPATH = "$scriptPath;$env:PYTHONPATH"

# Start the server with the correct working directory
Write-Host "Starting the server..."
Write-Host "Current directory: $(Get-Location)"
Write-Host "PYTHONPATH: $env:PYTHONPATH"

# Run the server with the correct working directory
$serverCommand = @"
import os
import sys
from uvicorn import run

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app
from app.main import app

# Run the server
run("app.main:app", host="0.0.0.0", port=8000, reload=True)
"@

$serverCommand | Out-File -FilePath "run_server.py" -Encoding utf8
python run_server.py 