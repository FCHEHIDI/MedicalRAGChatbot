#!/usr/bin/env python3
"""
🌐 AZURE DEPLOYMENT - SIMPLE & CLEAN
===================================
Entry point for Azure Web App deployment
"""

import os
import sys
import uvicorn

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    # Import your main FastAPI app
    from main import app
    
    # Azure provides the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Medical RAG Chatbot on Azure")
    print(f"🌐 Port: {port}")
    print(f"📊 API Docs: https://medical-rag-chatbot-fares.azurewebsites.net/docs")
    
    # Run the app
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )
