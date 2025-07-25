#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the model
ollama pull llama3.2:3b

# Start the FastAPI application
python main.py
