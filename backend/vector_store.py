"""
Pinecone Vector Store Implementation

This module handles all interactions with Pinecone vector database
for storing and retrieving medical knowledge embeddings.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pinecone import Pinecone, ServerlessSpec
import structlog
from openai import AsyncOpenAI
import tiktoken
from dataclasses import dataclass

logger = structlog.get_logger()

@dataclass
class Document:
    """Document class for storing text and metadata"""
    content: str
    metadata: Dict[str, Any]
    id: Optional[str] = None

@dataclass
class SearchResult:
    """Search result from vector database"""
    content: str
    score: float
    metadata: Dict[str, Any]
    id: str

class PineconeVectorStore:
    """
    Vector store implementation using Pinecone for medical knowledge storage
    """
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "medical-rag-index")
        self.dimension = int(os.getenv("PINECONE_DIMENSION", "1536"))
        
        # OpenAI client for embeddings
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # Pinecone client and index
        self.pc = None
        self.index = None
        
        # Tokenizer for text processing
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Configuration
        self.max_chunk_tokens = 8000  # Max tokens per chunk for embedding
        
    async def initialize(self):
        """Initialize Pinecone connection and index"""
        try:
            logger.info("Initializing Pinecone vector store...")
            
            if not self.api_key:
                raise ValueError("PINECONE_API_KEY not found in environment variables")
            
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready
                await asyncio.sleep(10)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            logger.info("Pinecone vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone vector store: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Pinecone vector store...")
        # Pinecone client handles cleanup automatically
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for given text using OpenAI"""
        try:
            # Check token count and truncate if necessary
            tokens = self.tokenizer.encode(text)
            if len(tokens) > self.max_chunk_tokens:
                logger.warning(f"Text too long ({len(tokens)} tokens), truncating to {self.max_chunk_tokens}")
                tokens = tokens[:self.max_chunk_tokens]
                text = self.tokenizer.decode(tokens)
            
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to create embedding: {str(e)}")
            raise
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store"""
        try:
            logger.info(f"Adding {len(documents)} documents to vector store...")
            
            if not self.index:
                raise ValueError("Vector store not initialized")
            
            # Process documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vectors = []
                
                for doc in batch:
                    # Create embedding
                    embedding = await self.create_embedding(doc.content)
                    
                    # Prepare vector for upsert
                    vector_id = doc.id or f"doc_{i}_{len(vectors)}"
                    metadata = {
                        **doc.metadata,
                        "content": doc.content[:1000],  # Store truncated content in metadata
                        "content_length": len(doc.content),
                        "embedding_model": self.embedding_model
                    }
                    
                    vectors.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    })
                
                # Upsert batch to Pinecone
                self.index.upsert(vectors=vectors)
                
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            logger.info("Successfully added all documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {str(e)}")
            raise
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        score_threshold: float = 0.7,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform similarity search in the vector store
        
        Args:
            query: Search query text
            k: Number of results to return
            score_threshold: Minimum similarity score threshold
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results
        """
        try:
            if not self.index:
                raise ValueError("Vector store not initialized")
            
            logger.info(f"Performing similarity search for query: {query[:100]}...")
            
            # Create query embedding
            query_embedding = await self.create_embedding(query)
            
            # Perform search
            search_kwargs = {
                "vector": query_embedding,
                "top_k": k,
                "include_metadata": True,
                "include_values": False
            }
            
            if filter_metadata:
                search_kwargs["filter"] = filter_metadata
            
            results = self.index.query(**search_kwargs)
            
            # Process results
            search_results = []
            for match in results.matches:
                if match.score >= score_threshold:
                    search_results.append(SearchResult(
                        content=match.metadata.get("content", ""),
                        score=float(match.score),
                        metadata=match.metadata,
                        id=match.id
                    ))
            
            logger.info(f"Found {len(search_results)} relevant documents (threshold: {score_threshold})")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            if not self.index:
                return {"status": "not_initialized"}
            
            stats = self.index.describe_index_stats()
            
            return {
                "status": "healthy",
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get vector store stats: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from vector store"""
        try:
            if not self.index:
                raise ValueError("Vector store not initialized")
            
            logger.info(f"Deleting {len(document_ids)} documents from vector store...")
            
            # Delete in batches
            batch_size = 1000
            for i in range(0, len(document_ids), batch_size):
                batch_ids = document_ids[i:i + batch_size]
                self.index.delete(ids=batch_ids)
            
            logger.info("Successfully deleted documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            raise
    
    async def update_document(self, document: Document) -> bool:
        """Update a single document in the vector store"""
        try:
            if not document.id:
                raise ValueError("Document ID is required for updates")
            
            # This is essentially the same as adding a document with a specific ID
            await self.add_documents([document])
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk
            overlap: Overlap between chunks in tokens
            
        Returns:
            List of text chunks
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            if end >= len(tokens):
                break
                
            start = end - overlap
        
        return chunks
    
    async def add_text_documents(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Add text documents with automatic chunking
        
        Args:
            texts: List of text documents
            metadatas: Optional list of metadata dicts
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks
            
        Returns:
            Success status
        """
        try:
            documents = []
            
            for i, text in enumerate(texts):
                metadata = metadatas[i] if metadatas else {}
                
                # Chunk the text
                chunks = self.chunk_text(text, chunk_size, chunk_overlap)
                
                for j, chunk in enumerate(chunks):
                    doc = Document(
                        content=chunk,
                        metadata={
                            **metadata,
                            "chunk_index": j,
                            "total_chunks": len(chunks),
                            "source_document_index": i
                        },
                        id=f"doc_{i}_chunk_{j}"
                    )
                    documents.append(doc)
            
            return await self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Failed to add text documents: {str(e)}")
            raise
