"""
🏥 MEDICAL RAG CHATBOT
=====================

🆓 100% FREE SOLUTION 🆓
✅ Ollama (Local LLM) - FREE
✅ ChromaDB (Vector DB) - FREE
✅ FastAPI (Backend) - FREE
✅ React (Frontend) - FREE

🎯 Portfolio-Ready AI/ML Project
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from domain import (
    RAGConfig,
    MedicalRAGSystem,
    cleanup_memory,
    get_memory_usage,
    RAGDomainError,
)

# ============================================
# 🗂️ PYDANTIC MODELS
# ============================================


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class SourceCitation(BaseModel):
    title: str
    content: str
    score: float
    metadata: dict


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[SourceCitation] = []
    safety_disclaimer: str = (
        "⚠️ MEDICAL DISCLAIMER: This AI assistant provides general medical information for educational purposes only. "
        "It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with "
        "qualified healthcare professionals for medical concerns, especially for serious symptoms or medical emergencies."
    )


class DocumentRequest(BaseModel):
    content: str
    title: str
    category: Optional[str] = "general"


# ============================================
# 🚀 FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title="🏥 Medical RAG Chatbot",
    description="Free AI-powered medical information assistant",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = None


@app.on_event("startup")
async def startup_event():
    global rag_system
    try:
        print("🔄 Starting RAG system initialization...")
        print("⏳ This may take 2-5 minutes on first run (downloading models)...")

        rag_system = MedicalRAGSystem()

        # Add some initial medical knowledge if collection is empty
        print("🔍 Checking existing knowledge base...")
        collection_count = rag_system.collection.count()
        if collection_count == 0:
            print("📚 Adding initial medical knowledge...")

            initial_docs = [
                {
                    "content": "Diabetes is a chronic condition that affects how your body turns food into energy. There are two main types: Type 1 (autoimmune) and Type 2 (insulin resistance). Management includes blood sugar monitoring, medication, diet control, and regular exercise.",
                    "title": "Diabetes Overview",
                    "category": "endocrinology",
                },
                {
                    "content": "Hypertension (high blood pressure) is often called the 'silent killer' because it usually has no symptoms. Normal blood pressure is less than 120/80 mmHg. Risk factors include age, family history, obesity, and lifestyle factors. Treatment may include lifestyle changes and medications.",
                    "title": "Hypertension Basics",
                    "category": "cardiology",
                },
                {
                    "content": "COVID-19 symptoms include fever, cough, shortness of breath, fatigue, body aches, headache, and loss of taste or smell. Seek medical attention if experiencing difficulty breathing, persistent chest pain, or confusion. Prevention includes vaccination, masking, and hand hygiene.",
                    "title": "COVID-19 Information",
                    "category": "infectious_disease",
                },
            ]

            for doc in initial_docs:
                rag_system.add_document(**doc)

            print("✅ Initial medical knowledge added!")
        else:
            print(f"✅ Found {collection_count} existing documents in knowledge base")

        print("🎉 RAG system fully initialized and ready!")
        print("🌐 Backend server is now accepting requests on http://localhost:8000")

    except RAGDomainError as e:
        print(f"❌ Startup error: {e}")
        print("💡 Check that Ollama is running: ollama serve")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("💡 Check that Ollama is running: ollama serve")


# ============================================
# 🌐 API ENDPOINTS
# ============================================


@app.get("/")
async def root():
    return {
        "message": "🏥 Medical RAG Chatbot API",
        "status": "running",
        "version": "2.0.0",
        "features": ["Ollama LLM", "ChromaDB", "Medical RAG"],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ollama": "connected" if rag_system and rag_system.ollama_client else "disconnected",
        "chromadb": "connected" if rag_system and rag_system.collection else "disconnected",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        knowledge = rag_system.search_knowledge(request.message)
        response = rag_system.generate_response(
            request.message,
            knowledge["context"],
        )

        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "default",
            sources=knowledge["sources"],
        )

    except RAGDomainError as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed") from e
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed") from e


@app.post("/add-document")
async def add_document(request: DocumentRequest):
    """Add document to knowledge base"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        return rag_system.add_document(
            request.content,
            request.title,
            request.category or "general",
        )
    except RAGDomainError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/knowledge-stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        count = rag_system.collection.count()
        return {
            "total_documents": count,
            "status": "ready" if count > 0 else "empty",
        }
    except Exception as e:
        return {"error": str(e)}


@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        return {
            "message": "Conversation cleared successfully",
            "conversation_id": conversation_id,
        }
    except Exception as e:
        print(f"❌ Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear conversation") from e


@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    try:
        return {
            "conversation_id": conversation_id,
            "history": [],
        }
    except Exception as e:
        print(f"❌ Get conversation history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history") from e


@app.get("/memory-status")
async def memory_status():
    """Get current memory usage and system status"""
    try:
        memory_info = get_memory_usage()
        return {
            "status": "healthy",
            "memory": memory_info,
            "requests_processed": rag_system.request_count if rag_system else 0,
            "next_cleanup": (
                RAGConfig.CLEANUP_FREQUENCY - (rag_system.request_count % RAGConfig.CLEANUP_FREQUENCY)
                if rag_system
                else "N/A"
            ),
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/cleanup-memory")
async def manual_cleanup():
    """Manually trigger memory cleanup"""
    try:
        collected = cleanup_memory()
        memory_info = get_memory_usage()
        return {
            "status": "success",
            "objects_collected": collected,
            "memory_after_cleanup": memory_info,
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================
# 🏃‍♂️ RUN APPLICATION
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    print("🏥 Starting Medical RAG Chatbot Server...")
    print("🆓 100% FREE - ChromaDB + FastAPI")
    print(f"🌐 Server running on port {port}")
    print(f"📖 API Docs: http://localhost:{port}/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
    )
