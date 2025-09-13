"""
Vector Database abstraction layer for RAG Pipeline.
Supports multiple vector database providers with a unified interface.
"""

from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class VectorDBInterface(ABC):
    """Abstract interface for vector database operations."""
    
    @abstractmethod
    def add_documents(self, embeddings: List[List[float]], documents: List[str], 
                     metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Add documents to the vector database."""
        pass
    
    @abstractmethod
    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """Query the vector database for similar documents."""
        pass
    
    @abstractmethod
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        pass
    
    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        pass


def create_vector_db(config: Dict[str, Any]) -> VectorDBInterface:
    """
    Factory function to create vector database instances.
    
    Args:
        config: Vector database configuration dictionary
        
    Returns:
        VectorDBInterface: Configured vector database instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = config.get('provider', 'chromadb').lower()
    
    if provider == 'chromadb':
        from .chromadb_client import ChromaDBVectorDB
        return ChromaDBVectorDB(config)
    elif provider == 'weaviate':
        from .weaviate_client import WeaviateVectorDB
        return WeaviateVectorDB(config)
    elif provider == 'qdrant':
        from .qdrant_client import QdrantVectorDB
        return QdrantVectorDB(config)
    else:
        raise ValueError(f"Unsupported vector database provider: {provider}")


def get_supported_providers() -> List[str]:
    """Get list of supported vector database providers."""
    return ['chromadb', 'weaviate', 'qdrant']
