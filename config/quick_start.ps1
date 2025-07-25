# Medical RAG Chatbot - Quick Start Script (PowerShell)
# This script provides a fast path to get the application running

Write-Host "🚀 Medical RAG Chatbot - Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 3.9+ is required but not installed" -ForegroundColor Red
    exit 1
}

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js 18+ is required but not installed" -ForegroundColor Red
    exit 1
}

# Check Ollama
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Ollama is required but not installed" -ForegroundColor Red
    Write-Host "   Please install from: https://ollama.com" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ All prerequisites met!" -ForegroundColor Green

# Setup environment
Write-Host "📁 Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item "config\.env.example" ".env"
    Write-Host "📝 Created .env file - please configure Ollama endpoint" -ForegroundColor Yellow
}

# Install backend dependencies
Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location ..\frontend
npm install

# Start Ollama model
Write-Host "🤖 Pulling Ollama model..." -ForegroundColor Yellow
Set-Location ..
ollama pull llama3.2:3b

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start the application:" -ForegroundColor Cyan
Write-Host "   Backend:  cd backend; uvicorn main:app --reload" -ForegroundColor White
Write-Host "   Frontend: cd frontend; npm start" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access at: http://localhost:3000" -ForegroundColor Green
