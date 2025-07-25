#!/bin/bash
# Medical RAG Chatbot - Quick Start Script
# This script provides a fast path to get the application running

echo "🚀 Medical RAG Chatbot - Quick Start"
echo "======================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.9+ is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ is required but not installed"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is required but not installed"
    echo "   Please install from: https://ollama.com"
    exit 1
fi

echo "✅ All prerequisites met!"

# Setup environment
echo "📁 Setting up environment..."
if [ ! -f ".env" ]; then
    cp config/.env.example .env
    echo "📝 Created .env file - please configure Ollama endpoint"
fi

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend && pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd ../frontend && npm install

# Start Ollama model
echo "🤖 Pulling Ollama model..."
ollama pull llama3.2:3b

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   Backend:  cd backend && uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm start"
echo ""
echo "🌐 Access at: http://localhost:3000"
