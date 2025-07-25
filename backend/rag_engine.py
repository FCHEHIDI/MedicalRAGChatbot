"""
Medical RAG Engine Implementation

This module implements the core RAG (Retrieval-Augmented Generation) functionality
for the Medical Chatbot, combining vector search with OpenAI GPT-4 for accurate
medical information retrieval and response generation.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import structlog
from openai import AsyncOpenAI
import tiktoken

from vector_store import PineconeVectorStore, SearchResult

logger = structlog.get_logger()

@dataclass
class ConversationMessage:
    """Message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[Dict[str, Any]]] = None

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, max_history_length: int = 10, context_window_hours: int = 24):
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.max_history_length = max_history_length
        self.context_window = timedelta(hours=context_window_hours)
    
    def add_message(self, conversation_id: str, message: ConversationMessage):
        """Add a message to conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append(message)
        
        # Cleanup old messages
        self._cleanup_conversation(conversation_id)
    
    def get_conversation(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history"""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def _cleanup_conversation(self, conversation_id: str):
        """Remove old messages from conversation"""
        if conversation_id not in self.conversations:
            return
        
        messages = self.conversations[conversation_id]
        cutoff_time = datetime.now() - self.context_window
        
        # Keep messages within time window and max length
        recent_messages = [
            msg for msg in messages 
            if msg.timestamp > cutoff_time
        ][-self.max_history_length:]
        
        self.conversations[conversation_id] = recent_messages

class MedicalRAGEngine:
    """
    Main RAG engine for medical question answering
    
    This class orchestrates the retrieval of relevant medical information
    and generates comprehensive responses using OpenAI GPT-4.
    """
    
    def __init__(self, vector_store: PineconeVectorStore):
        self.vector_store = vector_store
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Configuration
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.max_retrieval_docs = int(os.getenv("MAX_RETRIEVAL_DOCS", "5"))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
        
        # Conversation management
        self.conversation_manager = ConversationManager()
        
        # Tokenizer for context management
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        self.max_context_tokens = 8000  # Leave room for response
        
        # Medical safety settings
        self.enable_safety_disclaimer = os.getenv("ENABLE_SAFETY_DISCLAIMER", "True").lower() == "true"
        self.require_source_citations = os.getenv("REQUIRE_SOURCE_CITATIONS", "True").lower() == "true"
        
    async def initialize(self):
        """Initialize the RAG engine"""
        logger.info("Initializing Medical RAG Engine...")
        
        # Verify OpenAI connection
        try:
            await self.openai_client.models.list()
            logger.info("OpenAI connection verified")
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {str(e)}")
            raise
        
        logger.info("Medical RAG Engine initialized successfully")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Medical RAG Engine...")
        await self.openai_client.close()
    
    async def process_query(
        self, 
        query: str, 
        conversation_id: str,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Process a medical query using RAG
        
        Args:
            query: User's medical question
            conversation_id: Conversation identifier
            include_sources: Whether to include source citations
            
        Returns:
            Dictionary containing response, sources, and metadata
        """
        try:
            logger.info(f"Processing RAG query: {query[:100]}...")
            
            # Get conversation context
            conversation_history = self.conversation_manager.get_conversation(conversation_id)
            
            # Enhance query with conversation context if available
            enhanced_query = self._enhance_query_with_context(query, conversation_history)
            
            # Retrieve relevant documents
            retrieved_docs = await self._retrieve_relevant_documents(enhanced_query)
            
            # Generate response
            response_data = await self._generate_response(
                query, enhanced_query, retrieved_docs, conversation_history
            )
            
            # Store conversation
            self.conversation_manager.add_message(
                conversation_id,
                ConversationMessage(
                    role="user",
                    content=query,
                    timestamp=datetime.now()
                )
            )
            
            sources_data = [
                {
                    "title": self._extract_title_from_metadata(doc.metadata),
                    "content": doc.content,
                    "score": doc.score,
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ] if include_sources else []
            
            self.conversation_manager.add_message(
                conversation_id,
                ConversationMessage(
                    role="assistant",
                    content=response_data["response"],
                    timestamp=datetime.now(),
                    sources=sources_data
                )
            )
            
            return {
                "response": response_data["response"],
                "sources": sources_data,
                "metadata": {
                    "model_used": self.model,
                    "retrieval_docs_count": len(retrieved_docs),
                    "enhanced_query": enhanced_query,
                    "conversation_length": len(conversation_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {str(e)}")
            raise
    
    async def _retrieve_relevant_documents(self, query: str) -> List[SearchResult]:
        """Retrieve relevant documents from vector store"""
        try:
            logger.info("Retrieving relevant documents...")
            
            results = await self.vector_store.similarity_search(
                query=query,
                k=self.max_retrieval_docs,
                score_threshold=self.similarity_threshold
            )
            
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            # Return empty list to allow graceful degradation
            return []
    
    def _enhance_query_with_context(
        self, 
        query: str, 
        conversation_history: List[ConversationMessage]
    ) -> str:
        """Enhance query with conversation context"""
        if not conversation_history:
            return query
        
        # Get recent messages for context (last 3 exchanges)
        recent_messages = conversation_history[-6:]  # 3 user + 3 assistant messages
        
        context_parts = []
        for msg in recent_messages:
            if msg.role == "user":
                context_parts.append(f"Previous question: {msg.content}")
            elif msg.role == "assistant":
                # Include abbreviated response for context
                abbreviated_response = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                context_parts.append(f"Previous answer: {abbreviated_response}")
        
        if context_parts:
            context = "\n".join(context_parts)
            enhanced_query = f"Context from conversation:\n{context}\n\nCurrent question: {query}"
            return enhanced_query
        
        return query
    
    async def _generate_response(
        self,
        original_query: str,
        enhanced_query: str,
        retrieved_docs: List[SearchResult],
        conversation_history: List[ConversationMessage]
    ) -> Dict[str, str]:
        """Generate response using OpenAI GPT-4"""
        try:
            logger.info("Generating response with OpenAI...")
            
            # Prepare system prompt
            system_prompt = self._build_system_prompt()
            
            # Prepare context from retrieved documents
            context = self._build_context_from_documents(retrieved_docs)
            
            # Build user prompt
            user_prompt = self._build_user_prompt(original_query, context)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add conversation history if available (keep it concise)
            if conversation_history:
                history_context = self._build_conversation_context(conversation_history[-4:])  # Last 2 exchanges
                if history_context:
                    messages.insert(1, {"role": "system", "content": f"Conversation context:\n{history_context}"})
            
            # Ensure we don't exceed token limits
            messages = self._truncate_messages_to_fit_context(messages)
            
            # Generate response
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            
            generated_response = response.choices[0].message.content
            
            # Add safety disclaimer if enabled
            if self.enable_safety_disclaimer:
                generated_response = self._add_safety_disclaimer(generated_response)
            
            logger.info("Response generated successfully")
            
            return {
                "response": generated_response,
                "model": self.model,
                "usage": response.usage.dict() if response.usage else {}
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the AI assistant"""
        return """You are a knowledgeable medical AI assistant designed to provide accurate, helpful medical information. Your responses should be:

1. **Accurate and Evidence-Based**: Use only the provided medical context and established medical knowledge
2. **Clear and Accessible**: Explain medical concepts in understandable terms while maintaining accuracy
3. **Comprehensive**: Provide thorough answers that address the user's question completely
4. **Source-Aware**: Reference the provided medical sources when applicable
5. **Safety-Conscious**: Always emphasize the importance of professional medical consultation

Guidelines:
- Focus on educational information rather than diagnostic advice
- Acknowledge limitations when information is insufficient
- Use clear, professional medical terminology with explanations
- Structure responses logically with clear sections when appropriate
- Be empathetic and understanding of health concerns

Remember: You are providing educational information to help users understand medical topics, not replacing professional medical advice."""
    
    def _build_context_from_documents(self, documents: List[SearchResult]) -> str:
        """Build context string from retrieved documents"""
        if not documents:
            return "No specific medical references found for this query."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            title = self._extract_title_from_metadata(doc.metadata)
            context_parts.append(f"Source {i} - {title}:\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt with query and context"""
        return f"""Please answer the following medical question using the provided medical references and your medical knowledge:

QUESTION: {query}

MEDICAL REFERENCES:
{context}

Please provide a comprehensive, accurate response that:
1. Directly addresses the user's question
2. References relevant information from the medical sources when applicable
3. Explains medical concepts clearly
4. Maintains a helpful and professional tone

If the provided references don't contain sufficient information to fully answer the question, please indicate this and provide general medical knowledge while emphasizing the need for professional consultation."""
    
    def _build_conversation_context(self, messages: List[ConversationMessage]) -> str:
        """Build conversation context from recent messages"""
        context_parts = []
        
        for msg in messages:
            if msg.role == "user":
                context_parts.append(f"User asked: {msg.content}")
            elif msg.role == "assistant":
                # Abbreviated assistant response for context
                abbreviated = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                context_parts.append(f"Assistant replied: {abbreviated}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _truncate_messages_to_fit_context(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Truncate messages to fit within context window"""
        # Calculate total tokens
        total_tokens = sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)
        
        if total_tokens <= self.max_context_tokens:
            return messages
        
        # Keep system prompt and user query, truncate context
        system_msg = messages[0]
        context_msgs = messages[1:-1]
        user_msg = messages[-1]
        
        # Calculate tokens for required messages
        required_tokens = (
            len(self.tokenizer.encode(system_msg["content"])) + 
            len(self.tokenizer.encode(user_msg["content"]))
        )
        
        available_for_context = self.max_context_tokens - required_tokens
        
        # Truncate context messages to fit
        truncated_context = []
        current_tokens = 0
        
        for msg in reversed(context_msgs):  # Start from most recent
            msg_tokens = len(self.tokenizer.encode(msg["content"]))
            if current_tokens + msg_tokens <= available_for_context:
                truncated_context.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return [system_msg] + truncated_context + [user_msg]
    
    def _extract_title_from_metadata(self, metadata: Dict[str, Any]) -> str:
        """Extract title from document metadata"""
        return metadata.get("title", metadata.get("source", "Medical Knowledge Base"))
    
    def _add_safety_disclaimer(self, response: str) -> str:
        """Add medical safety disclaimer to response"""
        disclaimer = ("\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only "
                     "and should not replace professional medical advice, diagnosis, or treatment. "
                     "Always consult with qualified healthcare professionals for medical concerns. "
                     "In case of emergency, contact emergency services immediately.")
        
        return response + disclaimer
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get formatted conversation history"""
        messages = self.conversation_manager.get_conversation(conversation_id)
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "sources": msg.sources
            }
            for msg in messages
        ]
    
    async def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        self.conversation_manager.clear_conversation(conversation_id)
    
    async def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics"""
        return {
            "model": self.model,
            "active_conversations": len(self.conversation_manager.conversations),
            "max_retrieval_docs": self.max_retrieval_docs,
            "similarity_threshold": self.similarity_threshold,
            "safety_disclaimer_enabled": self.enable_safety_disclaimer,
            "source_citations_required": self.require_source_citations
        }
