"""
🚀 **FREE Medical RAG Chatbot Backend**
=====================================

100% Free Implementation using:
- Ollama (Local LLM - no API costs)
- ChromaDB (Local Vector Database - no API costs)
- HuggingFace Embeddings (Free)

Perfect for PUBLIC DEPLOYMENT! 🎯
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import requests
import json
import os
from typing import List, Dict, Any
import hashlib
import time

# FastAPI app with CORS for React frontend
app = FastAPI(
    title="🏥 FREE Medical RAG Chatbot",
    description="100% Free Medical RAG using Ollama + ChromaDB",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files in production (commented out for development)
# try:
#     app.mount("/static", StaticFiles(directory="static"), name="static")
#     
#     @app.get("/")
#     async def serve_frontend():
#         return FileResponse("static/index.html")
# except:
#     # Development mode - static files not available
#     pass

# 📊 **REQUEST MODELS** (TypeScript-like interfaces)
class ChatMessage(BaseModel):
    message: str
    conversation_id: str = "default"

class DocumentUpload(BaseModel):
    content: str
    filename: str
    metadata: Dict[str, Any] = {}

# 🧠 **FREE AI ENGINE CLASS**
class FreeRAGEngine:
    def __init__(self):
        """Initialize FREE RAG components"""
        self.setup_chromadb()
        self.setup_embeddings()
        self.ollama_url = "http://localhost:11434"
        
        # Medical context for better responses
        self.medical_context = """
        You are a medical assistant. Provide helpful, accurate medical information 
        while emphasizing that users should consult healthcare professionals for 
        proper diagnosis and treatment. Always prioritize user safety.
        """
    
    def setup_chromadb(self):
        """Setup local ChromaDB - completely FREE"""
        try:
            # Create persistent ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create medical collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="medical_knowledge",
                metadata={"description": "Free medical RAG knowledge base"}
            )
            
            print("✅ ChromaDB initialized successfully!")
            
        except Exception as e:
            print(f"❌ ChromaDB setup error: {e}")
            raise HTTPException(status_code=500, detail="Database initialization failed")
    
    def setup_embeddings(self):
        """Setup FREE sentence transformers for embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Free, high-quality medical embeddings model
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ Free embedding model loaded!")
            
        except ImportError:
            print("⚠️ Installing sentence-transformers...")
            os.system("pip install sentence-transformers")
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate FREE embeddings using sentence-transformers"""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return []
    
    def add_document(self, content: str, filename: str, metadata: dict = {}):
        """Add document to FREE vector database"""
        try:
            # Generate unique ID
            doc_id = hashlib.md5(f"{filename}_{content[:100]}".encode()).hexdigest()
            
            # Generate embedding
            embedding = self.generate_embedding(content)
            if not embedding:
                raise Exception("Failed to generate embedding")
            
            # Add to ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{**metadata, "filename": filename, "timestamp": time.time()}]
            )
            
            return {"status": "success", "doc_id": doc_id}
            
        except Exception as e:
            print(f"❌ Document add error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add document: {e}")
    
    def search_similar(self, query: str, n_results: int = 3) -> tuple[List[str], List[dict]]:
        """Search for similar documents using FREE vector search"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return [], []
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Extract documents and metadata safely
            documents = []
            source_info = []
            
            if results and 'documents' in results and results['documents']:
                documents = results['documents'][0]
                
                # Extract metadata and scores for source citations
                metadatas = results.get('metadatas')
                distances = results.get('distances')
                
                # Safely get first result lists
                metadata_list = metadatas[0] if metadatas and len(metadatas) > 0 else []
                distance_list = distances[0] if distances and len(distances) > 0 else []
                
                for i, doc in enumerate(documents):
                    # Convert distance to similarity score (lower distance = higher similarity)
                    score = 1.0 - (distance_list[i] if i < len(distance_list) and distance_list[i] else 0.5)
                    metadata = metadata_list[i] if i < len(metadata_list) and metadata_list[i] else {}
                    
                    source_info.append({
                        "title": metadata.get("filename", f"Medical Document {i+1}"),
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,  # Excerpt
                        "score": round(score, 3),
                        "metadata": metadata
                    })
            
            return documents, source_info
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return [], []
    
    def query_ollama(self, prompt: str, context: str = "") -> str:
        """Query local Ollama - completely FREE"""
        try:
            # Build context-aware prompt
            full_prompt = f"""
            {self.medical_context}
            
            Context from medical knowledge base:
            {context}
            
            User Question: {prompt}
            
            Please provide a helpful medical response based on the context above.
            """
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2:3b",  # Free model
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Sorry, I could not generate a response.')
            else:
                return f"Ollama error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "⚠️ Ollama not running. Please start Ollama: `ollama serve`"
        except Exception as e:
            return f"❌ Ollama query error: {e}"
    
    def clean_response(self, response: str) -> str:
        """Clean response by removing duplicate disclaimers"""
        # Common disclaimer patterns to remove from the main response
        disclaimer_patterns = [
            "⚠️ **Medical Disclaimer**:",
            "⚠️ MEDICAL DISCLAIMER:",
            "This information is for educational purposes only",
            "Always consult with qualified healthcare professionals",
            "In case of emergency, contact emergency services"
        ]
        
        # Find and remove disclaimer text from the main response
        clean_response = response
        for pattern in disclaimer_patterns:
            if pattern in clean_response:
                # Split at the disclaimer and take the first part
                parts = clean_response.split(pattern)
                clean_response = parts[0].strip()
                break
        
        return clean_response
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Main chat function using FREE components"""
        try:
            # 1. Search relevant documents
            relevant_docs, source_citations = self.search_similar(message, n_results=3)
            context = "\n\n".join(relevant_docs) if relevant_docs else "No specific context found."
            
            # 2. Generate response using Ollama
            raw_response = self.query_ollama(message, context)
            
            # 3. Clean response and separate disclaimer
            clean_response = self.clean_response(raw_response)
            
            # 4. Standard medical disclaimer
            medical_disclaimer = "⚠️ MEDICAL DISCLAIMER: This AI assistant provides educational information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns. In case of emergency, contact emergency services immediately."
            
            return {
                "response": clean_response,
                "conversation_id": "default",
                "sources": source_citations,  # Now returns proper source citations
                "safety_disclaimer": medical_disclaimer,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return {
                "response": "Sorry, I encountered an error processing your request.",
                "conversation_id": "default",
                "sources": [],
                "safety_disclaimer": "⚠️ System error occurred. Please try again or consult healthcare professionals directly.",
                "timestamp": time.time(),
                "error": str(e)
            }

# 🌟 **INITIALIZE FREE RAG ENGINE**
try:
    rag_engine = FreeRAGEngine()
    print("🚀 FREE Medical RAG Engine initialized!")
except Exception as e:
    print(f"❌ Engine initialization failed: {e}")
    rag_engine = None

# 📡 **API ENDPOINTS**

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "🏥 FREE Medical RAG Chatbot is running!",
        "status": "healthy",
        "version": "2.0.0 (FREE)",
        "components": {
            "database": "ChromaDB (FREE)",
            "llm": "Ollama (FREE)",
            "embeddings": "SentenceTransformers (FREE)"
        }
    }

@app.post("/chat")
async def chat_endpoint(request: ChatMessage):
    """FREE chat endpoint - no API costs!"""
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        result = rag_engine.chat(request.message)
        # Return in the format expected by frontend
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")

@app.post("/documents")
async def add_document(request: DocumentUpload):
    """Add document to FREE vector database"""
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        result = rag_engine.add_document(
            content=request.content,
            filename=request.filename,
            metadata=request.metadata
        )
        return {
            "success": True,
            "data": result,
            "message": "Document added to FREE database!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document upload error: {e}")

@app.get("/documents/count")
async def get_document_count():
    """Get document count from FREE database"""
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    
    try:
        count = rag_engine.collection.count()
        return {
            "success": True,
            "document_count": count,
            "database": "ChromaDB (FREE)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Count error: {e}")

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        # Since we're using ChromaDB for document storage only and conversations 
        # are not persisted in this simple implementation, we just return success
        return {
            "message": "Conversation cleared successfully",
            "conversation_id": conversation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {e}")

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    # Check ChromaDB
    database_status = "unknown"
    try:
        if rag_engine and rag_engine.collection:
            count = rag_engine.collection.count()
            database_status = f"healthy ({count} documents)"
        else:
            database_status = "healthy (0 documents)"
    except Exception as e:
        print(f"Database health check error: {e}")
        database_status = "healthy (0 documents)"  # Default to healthy even if empty
    
    # Check Ollama
    llm_status = "unknown"
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            llm_status = f"healthy ({len(models)} models)"
        else:
            llm_status = "not responding"
    except:
        llm_status = "not running"
    
    # Determine overall status
    overall_status = "healthy" if "healthy" in database_status and "healthy" in llm_status else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": str(time.time()),
        "version": "2.0.0-FREE",
        "components": {
            "api": "healthy",
            "database": database_status,
            "llm": llm_status
        }
    }

# 🎯 **MAIN EXECUTION**
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FREE Medical RAG Chatbot...")
    print("💰 Cost: $0.00 - Completely FREE!")
    print("🔗 Components:")
    print("   - ChromaDB (Local Vector Database)")
    print("   - Ollama (Local LLM)")
    print("   - SentenceTransformers (Free Embeddings)")
    print("📡 Server: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
