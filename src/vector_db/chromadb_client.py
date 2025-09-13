"""
ChromaDB implementation of the vector database interface.
"""

import chromadb
from typing import Dict, Any, List
import logging
from . import VectorDBInterface

logger = logging.getLogger(__name__)


class ChromaDBVectorDB(VectorDBInterface):
    """ChromaDB implementation of the vector database interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            config: ChromaDB configuration dictionary
        """
        self.config = config
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=config.get('path', './data/vectors')
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=config.get('collection_name', 'documents'),
            metadata={"hnsw:space": config.get('distance_metric', 'cosine')}
        )
        
        logger.info(f"ChromaDB initialized with collection: {self.collection.name}")
    
    def add_documents(self, embeddings: List[List[float]], documents: List[str], 
                     metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """
        Add documents to ChromaDB collection.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.debug(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """
        Query ChromaDB collection for similar documents.
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            
        Returns:
            Dictionary containing query results
        """
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            logger.debug(f"ChromaDB query returned {len(results.get('documents', [[]])[0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the ChromaDB collection.
        
        Returns:
            Dictionary containing collection information
        """
        try:
            count = self.collection.count()
            return {
                'name': self.collection.name,
                'count': count,
                'provider': 'chromadb',
                'metadata': self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting ChromaDB collection info: {e}")
            return {'name': 'unknown', 'count': 0, 'provider': 'chromadb'}
    
    def delete_collection(self) -> None:
        """Delete the ChromaDB collection."""
        try:
            self.client.delete_collection(self.collection.name)
            logger.info(f"Deleted ChromaDB collection: {self.collection.name}")
        except Exception as e:
            logger.error(f"Error deleting ChromaDB collection: {e}")
            raise
