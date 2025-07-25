"""
Data Ingestion Script for Medical RAG Chatbot

This script handles the ingestion of medical documents into the vector database.
Run this script to populate your knowledge base with medical information.
"""

import asyncio
import os
import sys
from pathlib import Path
import structlog

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from vector_store import PineconeVectorStore
from document_processor import MedicalDocumentProcessor

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

async def ingest_medical_data():
    """Main function to ingest medical data"""
    try:
        logger.info("Starting medical data ingestion...")
        
        # Initialize vector store
        vector_store = PineconeVectorStore()
        await vector_store.initialize()
        
        # Initialize document processor
        processor = MedicalDocumentProcessor(vector_store)
        
        # Add sample medical knowledge
        await processor.add_medical_knowledge_samples()
        
        # Check if data directory exists and process files
        data_dir = Path(__file__).parent.parent / "data"
        if data_dir.exists():
            logger.info(f"Processing files from {data_dir}")
            await processor.process_directory(str(data_dir))
        else:
            logger.info("No data directory found, using only sample data")
        
        # Get vector store stats
        stats = await vector_store.get_stats()
        logger.info("Ingestion complete", stats=stats)
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        raise
    finally:
        if 'vector_store' in locals():
            await vector_store.cleanup()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run ingestion
    asyncio.run(ingest_medical_data())
