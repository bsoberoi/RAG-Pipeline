"""
Weaviate implementation of the vector database interface.
"""

import weaviate
from typing import Dict, Any, List, Optional
import logging
import uuid
from . import VectorDBInterface

logger = logging.getLogger(__name__)


class WeaviateVectorDB(VectorDBInterface):
    """Weaviate implementation of the vector database interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Weaviate client and schema.
        
        Args:
            config: Weaviate configuration dictionary
        """
        self.config = config
        
        # Initialize Weaviate client
        url = config.get('url', 'http://localhost:8080')
        api_key = config.get('api_key')
        
        if api_key:
            self.client = weaviate.Client(
                url=url,
                auth_client_secret=weaviate.AuthApiKey(api_key=api_key)
            )
        else:
            self.client = weaviate.Client(url=url)
        
        self.class_name = config.get('class_name', 'Document')
        self.distance_metric = config.get('distance_metric', 'cosine')
        
        # Create schema if it doesn't exist
        self._create_schema()
        
        logger.info(f"Weaviate initialized with class: {self.class_name}")
    
    def _create_schema(self) -> None:
        """Create Weaviate schema if it doesn't exist."""
        try:
            # Check if class exists
            if self.client.schema.exists(self.class_name):
                logger.debug(f"Weaviate class {self.class_name} already exists")
                return
            
            # Define schema
            schema = {
                "class": self.class_name,
                "description": "Document chunks for RAG pipeline",
                "vectorizer": "none",  # We provide our own embeddings
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Document content"
                    },
                    {
                        "name": "filename",
                        "dataType": ["string"],
                        "description": "Source filename"
                    },
                    {
                        "name": "file_path",
                        "dataType": ["string"],
                        "description": "Full file path"
                    },
                    {
                        "name": "file_type",
                        "dataType": ["string"],
                        "description": "File type/extension"
                    },
                    {
                        "name": "chunk_id",
                        "dataType": ["int"],
                        "description": "Chunk identifier within document"
                    },
                    {
                        "name": "chunk_text",
                        "dataType": ["text"],
                        "description": "Preview of chunk text"
                    },
                    {
                        "name": "file_size",
                        "dataType": ["int"],
                        "description": "File size in bytes"
                    },
                    {
                        "name": "character_count",
                        "dataType": ["int"],
                        "description": "Character count of original document"
                    }
                ]
            }
            
            # Create class
            self.client.schema.create_class(schema)
            logger.info(f"Created Weaviate class: {self.class_name}")
            
        except Exception as e:
            logger.error(f"Error creating Weaviate schema: {e}")
            raise
    
    def add_documents(self, embeddings: List[List[float]], documents: List[str], 
                     metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """
        Add documents to Weaviate.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        try:
            # Prepare batch data
            batch_data = []
            for i, (embedding, document, metadata, doc_id) in enumerate(zip(embeddings, documents, metadatas, ids)):
                # Convert metadata to Weaviate format
                weaviate_metadata = {
                    "content": document,
                    "filename": metadata.get('filename', ''),
                    "file_path": metadata.get('file_path', ''),
                    "file_type": metadata.get('file_type', ''),
                    "chunk_id": metadata.get('chunk_id', i),
                    "chunk_text": metadata.get('chunk_text', document[:200] + "..." if len(document) > 200 else document),
                    "file_size": metadata.get('file_size', 0),
                    "character_count": metadata.get('character_count', len(document))
                }
                
                batch_data.append({
                    "id": doc_id,
                    "properties": weaviate_metadata,
                    "vector": embedding
                })
            
            # Batch insert
            with self.client.batch as batch:
                batch.batch_size = 100  # Process in batches of 100
                for item in batch_data:
                    batch.add_data_object(
                        data_object=item["properties"],
                        class_name=self.class_name,
                        uuid=item["id"],
                        vector=item["vector"]
                    )
            
            logger.debug(f"Added {len(documents)} documents to Weaviate")
            
        except Exception as e:
            logger.error(f"Error adding documents to Weaviate: {e}")
            raise
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> Dict[str, Any]:
        """
        Query Weaviate for similar documents.
        
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
            result = (
                self.client.query
                .get(self.class_name, ["content", "filename", "file_path", "file_type", 
                                     "chunk_id", "chunk_text", "file_size", "character_count"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(n_results)
                .with_additional(["distance"])
                .do()
            )
            
            # Convert to ChromaDB-compatible format
            if "data" in result and "Get" in result["data"]:
                weaviate_results = result["data"]["Get"][self.class_name]
                
                # Format results to match ChromaDB structure
                documents = []
                metadatas = []
                distances = []
                ids = []
                
                for item in weaviate_results:
                    documents.append(item["content"])
                    
                    # Reconstruct metadata
                    metadata = {
                        "filename": item.get("filename", ""),
                        "file_path": item.get("file_path", ""),
                        "file_type": item.get("file_type", ""),
                        "chunk_id": item.get("chunk_id", 0),
                        "chunk_text": item.get("chunk_text", ""),
                        "file_size": item.get("file_size", 0),
                        "character_count": item.get("character_count", 0)
                    }
                    metadatas.append(metadata)
                    
                    # Convert distance (Weaviate uses different distance metrics)
                    distance = item.get("_additional", {}).get("distance", 0.0)
                    distances.append(distance)
                    
                    # Generate ID (Weaviate doesn't return the original ID in this query)
                    ids.append(str(uuid.uuid4()))
                
                # Return in ChromaDB format
                result_dict = {
                    "documents": [documents],
                    "metadatas": [metadatas],
                    "distances": [distances],
                    "ids": [ids]
                }
                
                logger.debug(f"Weaviate query returned {len(documents)} results")
                return result_dict
            else:
                logger.warning("No results returned from Weaviate query")
                return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
                
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the Weaviate class.
        
        Returns:
            Dictionary containing class information
        """
        try:
            # Get class schema
            schema = self.client.schema.get(self.class_name)
            
            # Count objects (this is expensive for large datasets)
            count_result = (
                self.client.query
                .aggregate(self.class_name)
                .with_meta_count()
                .do()
            )
            
            count = 0
            if "data" in count_result and "Aggregate" in count_result["data"]:
                count = count_result["data"]["Aggregate"][self.class_name][0]["meta"]["count"]
            
            return {
                'name': self.class_name,
                'count': count,
                'provider': 'weaviate',
                'schema': schema
            }
        except Exception as e:
            logger.error(f"Error getting Weaviate class info: {e}")
            return {'name': self.class_name, 'count': 0, 'provider': 'weaviate'}
    
    def delete_collection(self) -> None:
        """Delete the Weaviate class."""
        try:
            self.client.schema.delete_class(self.class_name)
            logger.info(f"Deleted Weaviate class: {self.class_name}")
        except Exception as e:
            logger.error(f"Error deleting Weaviate class: {e}")
            raise
