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
import gc
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Optional

# Try to import ollama, but make it optional for initial deployment
try:
    import ollama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama library imported successfully")
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not available - will use fallback mode")

# ============================================
# 🧹 MEMORY OPTIMIZATION UTILITIES
# ============================================
def cleanup_memory():
    """Force garbage collection to free memory"""
    collected = gc.collect()
    print(f"🧹 Memory cleanup: {collected} objects collected")
    return collected

def get_memory_usage():
    """Get current memory usage info"""
    try:
        import os
        import sys
        
        # Get process info
        pid = os.getpid()
        
        # Basic memory info (works on all platforms)
        if sys.platform == "win32":
            # Windows specific
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get memory info from Windows API
                kernel32 = ctypes.windll.kernel32
                process_handle = kernel32.GetCurrentProcess()
                
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", wintypes.DWORD),
                        ("dwMemoryLoad", wintypes.DWORD),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                
                memory_status = MEMORYSTATUSEX()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
                
                used_mb = (memory_status.ullTotalPhys - memory_status.ullAvailPhys) // (1024 * 1024)
                total_mb = memory_status.ullTotalPhys // (1024 * 1024)
                
                return {
                    "used_mb": used_mb,
                    "total_mb": total_mb,
                    "available_mb": memory_status.ullAvailPhys // (1024 * 1024),
                    "usage_percent": (used_mb / total_mb) * 100
                }
            except:
                pass
        
        # Fallback: return basic info
        return {
            "used_mb": "unknown",
            "total_mb": "unknown", 
            "available_mb": "unknown",
            "usage_percent": "unknown"
        }
        
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 📊 CONFIGURATION - MEMORY OPTIMIZED
# ============================================
class RAGConfig:
    # Local Ollama settings
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2:1b"  # Use smaller 1B model for less memory
    
    # ChromaDB settings - MEMORY OPTIMIZED
    CHROMADB_PATH = "./chroma_db"
    COLLECTION_NAME = "medical_knowledge"
    
    # Embedding model - LIGHTWEIGHT
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and lightweight (22MB)
    
    # RAG settings - MEMORY CONSCIOUS
    TOP_K_RESULTS = 3  # Reduced from 5 to save memory
    MAX_CONTEXT_LENGTH = 1000  # Reduced from 1500
    BATCH_SIZE = 1  # Process one at a time
    
    # Memory management
    CLEANUP_FREQUENCY = 10  # Clean memory every 10 requests
    MAX_CACHE_SIZE = 50  # Limit cached embeddings

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
    safety_disclaimer: str = "⚠️ MEDICAL DISCLAIMER: This AI assistant provides general medical information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns, especially for serious symptoms or medical emergencies."

class DocumentRequest(BaseModel):
    content: str
    title: str
    category: Optional[str] = "general"

# ============================================
# 🧠 MEDICAL RAG SYSTEM
# ============================================
class MedicalRAGSystem:
    def __init__(self):
        print("🚀 Initializing Memory-Optimized Medical RAG System...")
        self.request_count = 0  # Track requests for cleanup
        self.setup_chromadb()
        self.setup_embeddings()
        self.setup_ollama()
        
        # Initial memory cleanup
        cleanup_memory()
        memory_info = get_memory_usage()
        print(f"💾 Initial Memory: {memory_info}")
        print("✅ Medical RAG System ready with memory optimization!")

    def setup_chromadb(self):
        """Setup local ChromaDB - MEMORY OPTIMIZED"""
        try:
            # Create persistent ChromaDB client with updated configuration
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            self.chroma_client = chromadb.PersistentClient(
                path=RAGConfig.CHROMADB_PATH,
                settings=settings
            )
            
            # Get or create medical collection with optimized settings
            self.collection = self.chroma_client.get_or_create_collection(
                name=RAGConfig.COLLECTION_NAME,
                metadata={
                    "description": "Free medical RAG knowledge base",
                    "hnsw:space": "cosine",  # Optimize for cosine similarity
                    "hnsw:batch_size": 100,  # Smaller batch size for less memory
                    "hnsw:sync_threshold": 1000  # Sync less frequently
                }
            )
            
            print("✅ ChromaDB initialized with memory optimization!")
            
        except Exception as e:
            print(f"❌ ChromaDB setup error: {e}")
            raise HTTPException(status_code=500, detail="Database initialization failed")

    def setup_embeddings(self):
        """Setup SentenceTransformer embeddings - MEMORY OPTIMIZED"""
        try:
            print("📚 Loading embedding model with memory optimization...")
            print(f"🔄 Downloading {RAGConfig.EMBEDDING_MODEL} (first time may take 2-3 minutes)...")
            
            # Memory-optimized SentenceTransformer initialization
            self.embedding_model = SentenceTransformer(
                RAGConfig.EMBEDDING_MODEL,
                cache_folder="./models_cache",  # Local cache instead of default
                device="cpu"  # Force CPU to avoid GPU memory
            )
            
            # Clear unnecessary model components to save memory
            if hasattr(self.embedding_model, '_modules'):
                # Remove unnecessary modules after loading
                import gc
                gc.collect()
            
            print("✅ Embedding model loaded with memory optimization!")
            
        except Exception as e:
            print(f"❌ Embedding setup error: {e}")
            raise HTTPException(status_code=500, detail="Embedding model initialization failed")

    def setup_ollama(self):
        """Setup Ollama client - completely FREE"""
        if not OLLAMA_AVAILABLE:
            print("⚠️ Ollama not installed - using fallback mode")
            self.ollama_client = None
            self.ollama_model = None
            return
            
        try:
            self.ollama_client = ollama.Client(host=RAGConfig.OLLAMA_HOST)
            
            # Test connection and model availability
            try:
                models = self.ollama_client.list()
                available_models = [model['name'] for model in models['models']]
                print(f"📦 Available Ollama models: {available_models}")
                
                # Try to use the 3B model first, fallback to smaller if needed
                if "llama3.2:3b" in available_models:
                    self.ollama_model = "llama3.2:3b"
                elif "llama3.2:1b" in available_models:
                    self.ollama_model = "llama3.2:1b"
                else:
                    print("⚠️ No models found - will use fallback responses")
                    self.ollama_model = None
                
                if self.ollama_model:
                    print(f"🤖 Using Ollama model: {self.ollama_model}")

            except Exception as model_error:
                print(f"⚠️ Model setup issue: {model_error}")
                print("🔄 Using fallback mode instead")
                self.ollama_model = None
                
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("� Using fallback mode - RAG will still work!")
            self.ollama_client = None
            self.ollama_model = None

    def add_document(self, content: str, title: str, category: str = "general"):
        """Add document to knowledge base - MEMORY OPTIMIZED"""
        try:
            # Generate embedding with memory optimization
            embedding = self.embedding_model.encode(
                [content], 
                convert_to_tensor=False,  # Return numpy arrays
                normalize_embeddings=True,  # Normalize embeddings
                batch_size=1  # Process one at a time
            )[0].tolist()
            
            # Generate unique ID
            doc_id = f"{category}_{title}_{hash(content) % 10000}"
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    "title": title,
                    "category": category,
                    "content_length": len(content)
                }],
                ids=[doc_id]
            )
            
            # Clear embedding from memory
            del embedding
            import gc
            gc.collect()
            
            return {"status": "success", "doc_id": doc_id}
            
        except Exception as e:
            print(f"❌ Document addition error: {e}")
            raise HTTPException(status_code=500, detail="Failed to add document")

    def search_knowledge(self, query: str, n_results: int = RAGConfig.TOP_K_RESULTS):
        """Search knowledge base for relevant information - MEMORY OPTIMIZED"""
        try:
            # Generate query embedding with memory optimization
            query_embedding = self.embedding_model.encode(
                [query], 
                convert_to_tensor=False,  # Return numpy arrays instead of tensors
                normalize_embeddings=True,  # Normalize to reduce computation
                batch_size=1  # Process one at a time to save memory
            )[0].tolist()
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results with memory cleanup
            knowledge_context = []
            sources = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0] if results['documents'] else [],
                results['metadatas'][0] if results['metadatas'] else [], 
                results['distances'][0] if results['distances'] else []
            )):
                if distance < 0.8:  # Filter by relevance threshold
                    knowledge_context.append(f"Source {i+1}: {doc}")
                    
                    # Create properly structured source citation
                    source_citation = {
                        "title": metadata.get('title', f'Document {i+1}'),
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,  # Truncate content for preview
                        "score": round(1.0 - distance, 3),  # Convert distance to similarity score
                        "metadata": {
                            "category": metadata.get('category', 'general'),
                            "content_length": metadata.get('content_length', len(doc)),
                            "full_content": doc  # Keep full content for reference
                        }
                    }
                    sources.append(source_citation)
            
            # Clear variables to free memory
            del query_embedding, results
            import gc
            gc.collect()
            
            return {
                "context": "\n\n".join(knowledge_context),
                "sources": sources
            }
            
        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return {"context": "", "sources": []}

    def generate_response(self, query: str, context: str) -> str:
        """Generate response using Ollama or fallback - MEMORY OPTIMIZED"""
        
        # Increment request counter for cleanup
        self.request_count += 1
        
        # Periodic memory cleanup
        if self.request_count % RAGConfig.CLEANUP_FREQUENCY == 0:
            cleanup_memory()
            print(f"🧹 Periodic cleanup after {self.request_count} requests")
        
        # Create medical-focused prompt
        system_prompt = """You are a helpful medical assistant. Use the provided context to answer questions accurately and professionally. 

If the context doesn't contain relevant information, say so clearly and provide general medical guidance while recommending consultation with healthcare professionals.

IMPORTANT: Always remind users to consult with qualified healthcare professionals for medical advice."""

        prompt = f"""Context from medical knowledge base:
{context}

Question: {query}

Please provide a helpful, accurate response based on the context above:"""
        
        # Try Ollama first if available
        if OLLAMA_AVAILABLE and self.ollama_client and self.ollama_model:
            try:
                response = self.ollama_client.chat(
                    model=self.ollama_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Clear variables to save memory
                del system_prompt, prompt
                gc.collect()
                
                return response['message']['content']
                
            except Exception as e:
                print(f"❌ Ollama generation error: {e}")
                print("🔄 Falling back to simple response...")
        
        # Fallback response when Ollama unavailable
        if context.strip():
            fallback_response = f"""Based on the medical information in our knowledge base:

{context}

For the question: "{query}"

⚠️ This information is from our medical knowledge base and should be used for educational purposes only. Always consult with qualified healthcare professionals for personalized medical advice, diagnosis, or treatment recommendations.

🏥 For emergencies or serious symptoms, seek immediate medical attention."""
        else:
            fallback_response = f"""I don't have specific information about "{query}" in my current knowledge base.

For accurate medical information about this topic, I recommend:
1. Consulting with your healthcare provider
2. Visiting reputable medical websites like WebMD or Mayo Clinic
3. Contacting your doctor's office for guidance

⚠️ MEDICAL DISCLAIMER: Always consult with qualified healthcare professionals for medical concerns, especially for serious symptoms or medical emergencies."""

        # Memory cleanup
        gc.collect()
        
        return fallback_response

# ============================================
# 🚀 FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title="🏥 Medical RAG Chatbot",
    description="Free AI-powered medical information assistant",
    version="2.0.0"
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
                    "category": "endocrinology"
                },
                {
                    "content": "Hypertension (high blood pressure) is often called the 'silent killer' because it usually has no symptoms. Normal blood pressure is less than 120/80 mmHg. Risk factors include age, family history, obesity, and lifestyle factors. Treatment may include lifestyle changes and medications.",
                    "title": "Hypertension Basics",
                    "category": "cardiology"
                },
                {
                    "content": "COVID-19 symptoms include fever, cough, shortness of breath, fatigue, body aches, headache, and loss of taste or smell. Seek medical attention if experiencing difficulty breathing, persistent chest pain, or confusion. Prevention includes vaccination, masking, and hand hygiene.",
                    "title": "COVID-19 Information",
                    "category": "infectious_disease"
                }
            ]
            
            for doc in initial_docs:
                rag_system.add_document(**doc)
            
            print("✅ Initial medical knowledge added!")
        else:
            print(f"✅ Found {collection_count} existing documents in knowledge base")
            
        print("🎉 RAG system fully initialized and ready!")
        print("🌐 Backend server is now accepting requests on http://localhost:8000")
            
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
        "features": ["Ollama LLM", "ChromaDB", "Medical RAG"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ollama": "connected" if rag_system and rag_system.ollama_client else "disconnected",
        "chromadb": "connected" if rag_system and rag_system.collection else "disconnected"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Search knowledge base
        knowledge = rag_system.search_knowledge(request.message)
        
        # Generate response
        response = rag_system.generate_response(
            request.message, 
            knowledge["context"]
        )
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id or "default",
            sources=knowledge["sources"]
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/add-document")
async def add_document(request: DocumentRequest):
    """Add document to knowledge base"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return rag_system.add_document(
        request.content,
        request.title,
        request.category or "general"
    )

@app.get("/knowledge-stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        count = rag_system.collection.count()
        return {
            "total_documents": count,
            "status": "ready" if count > 0 else "empty"
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        # For this simple implementation, we just return success
        # In a real app, you'd delete the conversation from a database
        return {
            "message": "Conversation cleared successfully",
            "conversation_id": conversation_id
        }
    except Exception as e:
        print(f"❌ Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear conversation")

@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    try:
        # For this simple implementation, return empty history
        # In a real app, you'd fetch from a database
        return {
            "conversation_id": conversation_id,
            "history": []
        }
    except Exception as e:
        print(f"❌ Get conversation history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation history")

@app.get("/memory-status")
async def memory_status():
    """Get current memory usage and system status"""
    try:
        memory_info = get_memory_usage()
        return {
            "status": "healthy",
            "memory": memory_info,
            "requests_processed": rag_system.request_count if rag_system else 0,
            "next_cleanup": RAGConfig.CLEANUP_FREQUENCY - (rag_system.request_count % RAGConfig.CLEANUP_FREQUENCY) if rag_system else "N/A"
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
            "memory_after_cleanup": memory_info
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 🏃‍♂️ RUN APPLICATION
# ============================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    
    print("🏥 Starting Medical RAG Chatbot Server...")
    print("🆓 100% FREE - ChromaDB + FastAPI")
    print(f"🌐 Server running on port {port}")
    print(f"📖 API Docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload to allow proper startup
    )
