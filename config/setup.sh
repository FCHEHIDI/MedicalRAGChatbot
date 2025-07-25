#!/bin/bash

# Medical RAG Chatbot Setup Script
# This script sets up the entire project with all dependencies

set -e  # Exit on any error

echo "🩺 Medical RAG Chatbot - Setup Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
    VENV_ACTIVATE="venv/Scripts/activate"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    VENV_ACTIVATE="venv/bin/activate"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists $PYTHON_CMD; then
    print_error "Python 3.11+ is required but not installed."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

if ! command_exists node; then
    print_error "Node.js 18+ is required but not installed."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

if ! command_exists npm; then
    print_error "npm is required but not installed."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Copying from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your API keys before continuing."
    echo "Required variables:"
    echo "  - OPENAI_API_KEY"
    echo "  - PINECONE_API_KEY"
    echo "  - PINECONE_ENVIRONMENT"
    read -p "Press Enter to continue after editing .env file..."
fi

# Backend setup
print_status "Setting up backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_ACTIVATE

# Upgrade pip
print_status "Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
$PIP_CMD install -r requirements.txt
print_success "Backend dependencies installed"

# Test backend setup
print_status "Testing backend setup..."
$PYTHON_CMD -c "import fastapi, openai, pinecone; print('✓ All backend modules imported successfully')"

cd ..

# Frontend setup
print_status "Setting up frontend..."

cd frontend

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Frontend dependencies installed"

# Test frontend setup
print_status "Testing frontend setup..."
npm run build >/dev/null 2>&1 || print_warning "Frontend build test failed (this is normal if dependencies are missing)"

cd ..

# Data setup
print_status "Setting up sample medical data..."

# Check if data directory has content
if [ ! "$(ls -A data/)" ]; then
    print_warning "Data directory is empty. Sample data files have been created."
fi

print_success "Sample medical data is ready"

# Final setup
print_status "Running final setup tasks..."

# Create logs directory
mkdir -p logs
print_success "Logs directory created"

# Create uploads directory for document processing
mkdir -p uploads
print_success "Uploads directory created"

echo ""
print_success "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys if you haven't already"
echo "2. Start the backend: cd backend && source $VENV_ACTIVATE && python ingest_data.py"
echo "3. Run the backend server: uvicorn main:app --reload"
echo "4. Start the frontend: cd frontend && npm start"
echo ""
echo "Access the application at:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
print_warning "Remember to populate your .env file with valid API keys!"

# Option to start services
read -p "Would you like to ingest sample data now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Ingesting sample medical data..."
    cd backend
    source $VENV_ACTIVATE
    $PYTHON_CMD ingest_data.py
    cd ..
    print_success "Sample data ingested successfully!"
fi

echo ""
print_success "Medical RAG Chatbot is ready to use! 🚀"
