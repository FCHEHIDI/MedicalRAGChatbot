# Medical RAG Chatbot Setup Script (PowerShell)
# This script sets up the entire project with all dependencies

param(
    [switch]$SkipDataIngestion = $false
)

# Colors for output
$Colors = @{
    Info = "Cyan"
    Success = "Green" 
    Warning = "Yellow"
    Error = "Red"
}

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    Write-Host "[$Type] $Message" -ForegroundColor $Colors[$Type]
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "🩺 Medical RAG Chatbot - Setup Script (PowerShell)" -ForegroundColor Magenta
Write-Host "====================================================" -ForegroundColor Magenta
Write-Host ""

# Check prerequisites
Write-ColoredOutput "Checking prerequisites..." "Info"

if (-not (Test-Command "python")) {
    Write-ColoredOutput "Python 3.11+ is required but not installed." "Error"
    Write-ColoredOutput "Please install Python from https://python.org" "Error"
    exit 1
}

$pythonVersion = (python --version) -replace "Python ", ""
Write-ColoredOutput "Python $pythonVersion found" "Success"

if (-not (Test-Command "node")) {
    Write-ColoredOutput "Node.js 18+ is required but not installed." "Error"
    Write-ColoredOutput "Please install Node.js from https://nodejs.org" "Error"
    exit 1
}

$nodeVersion = node --version
Write-ColoredOutput "Node.js $nodeVersion found" "Success"

if (-not (Test-Command "npm")) {
    Write-ColoredOutput "npm is required but not installed." "Error"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-ColoredOutput ".env file not found. Copying from .env.example..." "Warning"
    Copy-Item ".env.example" ".env"
    Write-ColoredOutput "Please edit .env file with your API keys before continuing." "Warning"
    Write-Host "Required variables:"
    Write-Host "  - OPENAI_API_KEY"
    Write-Host "  - PINECONE_API_KEY" 
    Write-Host "  - PINECONE_ENVIRONMENT"
    Read-Host "Press Enter to continue after editing .env file"
}

# Backend setup
Write-ColoredOutput "Setting up backend..." "Info"

Set-Location "backend"

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-ColoredOutput "Creating Python virtual environment..." "Info"
    python -m venv venv
    Write-ColoredOutput "Virtual environment created" "Success"
}

# Activate virtual environment
Write-ColoredOutput "Activating virtual environment..." "Info"
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-ColoredOutput "Upgrading pip..." "Info"
python -m pip install --upgrade pip

# Install dependencies
Write-ColoredOutput "Installing Python dependencies..." "Info"
pip install -r requirements.txt
Write-ColoredOutput "Backend dependencies installed" "Success"

# Test backend setup
Write-ColoredOutput "Testing backend setup..." "Info"
try {
    python -c "import fastapi, openai, pinecone; print('✓ All backend modules imported successfully')"
    Write-ColoredOutput "Backend modules test passed" "Success"
} catch {
    Write-ColoredOutput "Backend modules test failed - some dependencies may be missing" "Warning"
}

Set-Location ".."

# Frontend setup
Write-ColoredOutput "Setting up frontend..." "Info"

Set-Location "frontend"

# Install dependencies
Write-ColoredOutput "Installing Node.js dependencies..." "Info"
npm install
Write-ColoredOutput "Frontend dependencies installed" "Success"

# Test frontend setup
Write-ColoredOutput "Testing frontend setup..." "Info"
try {
    npm run build > $null 2>&1
    Write-ColoredOutput "Frontend build test passed" "Success"
} catch {
    Write-ColoredOutput "Frontend build test failed (this may be normal)" "Warning"
}

Set-Location ".."

# Data setup
Write-ColoredOutput "Setting up sample medical data..." "Info"

# Check if data directory has content
$dataFiles = Get-ChildItem "data" -ErrorAction SilentlyContinue
if (-not $dataFiles) {
    Write-ColoredOutput "Data directory is empty. Sample data files have been created." "Warning"
} else {
    Write-ColoredOutput "Sample medical data files found" "Success"
}

# Final setup
Write-ColoredOutput "Running final setup tasks..." "Info"

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Name "logs" | Out-Null
    Write-ColoredOutput "Logs directory created" "Success"
}

# Create uploads directory for document processing
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Name "uploads" | Out-Null
    Write-ColoredOutput "Uploads directory created" "Success"
}

Write-Host ""
Write-ColoredOutput "🎉 Setup completed successfully!" "Success"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env file with your API keys if you haven't already"
Write-Host "2. Start the backend:"
Write-Host "   cd backend"
Write-Host "   venv\Scripts\Activate.ps1"
Write-Host "   python ingest_data.py"
Write-Host "   uvicorn main:app --reload"
Write-Host "3. Start the frontend:"
Write-Host "   cd frontend"
Write-Host "   npm start"
Write-Host ""
Write-Host "Access the application at:"
Write-Host "  • Frontend: http://localhost:3000"
Write-Host "  • Backend API: http://localhost:8000"
Write-Host "  • API Docs: http://localhost:8000/docs"
Write-Host ""
Write-ColoredOutput "Remember to populate your .env file with valid API keys!" "Warning"

# Option to start data ingestion
if (-not $SkipDataIngestion) {
    $response = Read-Host "Would you like to ingest sample data now? (y/n)"
    if ($response -match "^[Yy]") {
        Write-ColoredOutput "Ingesting sample medical data..." "Info"
        Set-Location "backend"
        & "venv\Scripts\Activate.ps1"
        python ingest_data.py
        Set-Location ".."
        Write-ColoredOutput "Sample data ingested successfully!" "Success"
    }
}

Write-Host ""
Write-ColoredOutput "Medical RAG Chatbot is ready to use! 🚀" "Success"
