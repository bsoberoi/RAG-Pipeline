"""
Qdrant implementation of the vector database interface.
"""

import qdrant_client
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import Dict, Any, List
import logging
import uuid
from . import VectorDBInterface

logger = logging.getLogger(__name__)


class QdrantVectorDB(VectorDBInterface):
    """Qdrant implementation of the vector database interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant client and collection.
        
        Args:
            config: Qdrant configuration dictionary
        """
        self.config = config
        
        # Initialize Qdrant client
        # Use qdrant_url if available, otherwise fall back to url
        url = config.get('qdrant_url') or config.get('url', 'http://localhost:6333')
        api_key = config.get('qdrant_api_key') or config.get('api_key')
        
        if api_key:
            self.client = qdrant_client.QdrantClient(
                url=url,
                api_key=api_key
            )
        else:
            self.client = qdrant_client.QdrantClient(url=url)
        
        self.collection_name = config.get('collection_name', 'documents')
        self.distance_metric = config.get('distance_metric', 'cosine')
        self.vector_size = config.get('vector_size', 384)  # Default for sentence-transformers
        
        # Create collection if it doesn't exist
        self._create_collection()
        
        logger.info(f"Qdrant initialized with collection: {self.collection_name}")
    
    def _create_collection(self) -> None:
        """Create Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.debug(f"Qdrant collection {self.collection_name} already exists")
                return
            
            # Map distance metrics
            distance_mapping = {
                'cosine': Distance.COSINE,
                'euclidean': Distance.EUCLID,
                'dot': Distance.DOT
            }
            
            distance = distance_mapping.get(self.distance_metric, Distance.COSINE)
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=distance
                )
            )
            
            logger.info(f"Created Qdrant collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
            raise
    
    def add_documents(self, embeddings: List[List[float]], documents: List[str], 
                     metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """
        Add documents to Qdrant.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        try:
            # Prepare points for Qdrant
            points = []
            for i, (embedding, document, metadata, doc_id) in enumerate(zip(embeddings, documents, metadatas, ids)):
                # Convert metadata to Qdrant format
                qdrant_metadata = {
                    "content": document,
                    "filename": metadata.get('filename', ''),
                    "file_path": metadata.get('file_path', ''),
                    "file_type": metadata.get('file_type', ''),
                    "chunk_id": metadata.get('chunk_id', i),
                    "chunk_text": metadata.get('chunk_text', document[:200] + "..." if len(document) > 200 else document),
                    "file_size": metadata.get('file_size', 0),
                    "character_count": metadata.get('character_count', len(document))
                }
                
                # Create point with proper ID handling (Qdrant requires UUID or integer)
                if doc_id and doc_id.isdigit():
                    point_id = int(doc_id)
                else:
                    point_id = str(uuid.uuid4())
                
                # Create point
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=qdrant_metadata
                )
                points.append(point)
            
            # Upsert points to Qdrant using the correct API
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.debug(f"Added {len(documents)} documents to Qdrant")
            
        except Exception as e:
            logger.error(f"Error adding documents to Qdrant: {e}")
            raise
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """
        Query Qdrant for similar documents.
        
        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            
        Returns:
            Dictionary containing query results in ChromaDB-compatible format
        """
        try:
            # Use the first query embedding (ChromaDB interface expects single query)
            query_embedding = query_embeddings[0]
            
            # Perform vector search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=n_results,
                with_payload=True
            )
            
            # Convert to ChromaDB-compatible format
            documents = []
            metadatas = []
            distances = []
            ids = []
            
            for result in search_results:
                # Extract document content
                payload = result.payload
                documents.append(payload.get('content', ''))
                
                # Reconstruct metadata
                metadata = {
                    "filename": payload.get('filename', ''),
                    "file_path": payload.get('file_path', ''),
                    "file_type": payload.get('file_type', ''),
                    "chunk_id": payload.get('chunk_id', 0),
                    "chunk_text": payload.get('chunk_text', ''),
                    "file_size": payload.get('file_size', 0),
                    "character_count": payload.get('character_count', 0)
                }
                metadatas.append(metadata)
                
                # Convert distance (Qdrant uses different distance metrics)
                distance = result.score
                distances.append(distance)
                
                # Use result ID
                ids.append(str(result.id))
            
            # Return in ChromaDB format
            result_dict = {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [ids]
            }
            
            logger.debug(f"Qdrant query returned {len(documents)} results")
            return result_dict
                
        except Exception as e:
            logger.error(f"Error querying Qdrant: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the Qdrant collection.
        
        Returns:
            Dictionary containing collection information
        """
        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            
            # Count points (this is expensive for large datasets)
            count_result = self.client.count(self.collection_name)
            count = count_result.count
            
            return {
                'name': self.collection_name,
                'count': count,
                'provider': 'qdrant',
                'vector_size': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance.name.lower()
            }
        except Exception as e:
            logger.error(f"Error getting Qdrant collection info: {e}")
            return {'name': self.collection_name, 'count': 0, 'provider': 'qdrant'}
    
    def delete_collection(self) -> None:
        """Delete the Qdrant collection."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting Qdrant collection: {e}")
            raise
