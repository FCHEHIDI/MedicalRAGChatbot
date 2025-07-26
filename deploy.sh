#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Azure deployment for Medical RAG Chatbot..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:./backend"

# Create virtual environment if it doesn't exist
if [ ! -d "antenv" ]; then
    echo "� Creating virtual environment..."
    python -m venv antenv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source antenv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"
echo "🏥 Medical RAG Chatbot deployment completed!"
