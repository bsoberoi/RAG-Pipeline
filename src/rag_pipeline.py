"""Main RAG Pipeline - Integrates all components for end-to-end functionality."""

import os
import logging
from typing import List, Dict, Any, Optional

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

# Local imports
from src.utils.config_loader import ConfigLoader
from src.utils.log_manager import LogManager
from src.vector_db import create_vector_db, VectorDBInterface
from src.ingestion.document_loader import DocumentLoader


class RAGPipeline:
    """Complete RAG pipeline for document-based question answering."""
    
    def __init__(self, config_path: str = ""):
        """
        Initialize the RAG pipeline.
        
        Args:
            config_path: Path to configuration file
        """

        
        # Always resolve config_path relative to the project root
        if not config_path:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, "config", "config.yaml")
        self.config = ConfigLoader(config_path)
        
        # Get logging path from config
        log_path = self.config.get('logging.path', './logs')
        
        # Ensure log directory exists before creating log file
        LogManager.ensure_log_directory(log_path)
        
        # Use LogManager for consistent timestamped log filename
        log_file = LogManager.get_log_filepath(log_dir=log_path)
        
        log_level_str = self.config.get('logging.level', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        # Check if logging is already configured (from log_manager)
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=log_level,
                format=self.config.get('logging.format', LogManager.get_default_format()),
                handlers=[
                    logging.FileHandler(log_file, mode='w', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
        
        self.logger = logging.getLogger(__name__)
        
        # Log initialization message only to file (not console)
        file_logger = logging.getLogger('rag_file_only')
        file_logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(self.config.get('logging.format', LogManager.get_default_format())))
        file_logger.addHandler(file_handler)
        file_logger.propagate = False  # Prevent propagation to root logger (which has console handler)
        file_logger.info(f"RAGPipeline: Logging initialized. Log file: {log_file}")
        
        # Initialize components
        self.logger.debug("Initializing DocumentLoader...")
        self.document_loader = DocumentLoader()
        self.logger.debug("Initializing TextSplitter...")
        self.text_splitter = self._setup_text_splitter()
        self.logger.debug("Initializing Embeddings...")
        self.embeddings = self._setup_embeddings()
        self.logger.debug("Initializing VectorDB...")
        self.vector_db = self._setup_vector_db()
        self.logger.debug("Initializing LLM...")
        self.llm = self._setup_llm()
        
        # Log successful initialization only to file (not console)
        file_logger.info("RAG Pipeline initialized successfully")
    
    def _setup_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Set up the text splitter with configuration."""
        config = self.config.get_text_splitter_config()
        
        return RecursiveCharacterTextSplitter(
            chunk_size=config.get('chunk_size', 1000),
            chunk_overlap=config.get('chunk_overlap', 200),
            separators=config.get('separators', ["\n\n", "\n", " ", ""])
        )
    
    def _setup_embeddings(self) -> HuggingFaceEmbeddings:
        """Set up the embedding model."""
        config = self.config.get_embeddings_config()
        
        return HuggingFaceEmbeddings(
            model_name=config.get('model', 'sentence-transformers/all-MiniLM-L6-v2')
        )
    
    def _setup_vector_db(self) -> VectorDBInterface:
        """Set up vector database using the configured provider."""
        config = self.config.get_vector_db_config()
        
        # Create vector database instance using factory
        vector_db = create_vector_db(config)
        
        return vector_db
    
    def _setup_llm(self) -> ChatGroq:
        """Set up the language model."""
        config = self.config.get_llm_config()
        
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        return ChatGroq(
            model=config.get('model', 'llama-3.1-8b-instant'),
            temperature=config.get('temperature', 0.7),
            max_tokens=config.get('max_tokens', 1000),
            api_key=SecretStr(api_key)
        )
    
    def ingest_document(self, file_path: str) -> None:
        self.logger.info(f"Ingesting document: {file_path}")
        # Load document
        doc_data = self.document_loader.load_document(file_path)
        
        # Handle both single documents and lists of documents (from JSON files)
        if isinstance(doc_data, list):
            # Process each document in the list
            total_chunks = 0
            for doc in doc_data:
                chunks = self._process_single_document(doc)
                total_chunks += len(chunks)
            self.logger.info(f"Ingested {total_chunks} chunks from {file_path}")
        else:
            # Process single document
            chunks = self._process_single_document(doc_data)
            self.logger.info(f"Ingested {len(chunks)} chunks from {file_path}")
    
    def _process_single_document(self, doc_data: dict) -> list:
        """Process a single document and add it to the vector database."""
        # Split text into chunks
        chunks = self.text_splitter.split_text(doc_data['content'])
        
        # Generate embeddings and store in vector database
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.embeddings.embed_query(chunk)
            
            # Create metadata
            metadata = doc_data['metadata'].copy()
            metadata.update({
                'chunk_id': i,
                'chunk_text': chunk[:200] + "..." if len(chunk) > 200 else chunk
            })
            
            # Add to vector database
            self.vector_db.add_documents(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata],
                ids=[f"{metadata['filename']}_chunk_{i}"]
            )
        
        return chunks
    
    def ingest_directory(self, directory_path: str) -> None:
        self.logger.info(f"Ingesting all documents from directory: {directory_path}")
        documents = self.document_loader.load_directory(directory_path)
        
        for doc_data in documents:
            # Split text into chunks
            chunks = self.text_splitter.split_text(doc_data['content'])
            
            # Process chunks
            for i, chunk in enumerate(chunks):
                embedding = self.embeddings.embed_query(chunk)
                
                metadata = doc_data['metadata'].copy()
                metadata.update({
                    'chunk_id': i,
                    'chunk_text': chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
                
                self.vector_db.add_documents(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[f"{metadata['filename']}_chunk_{i}"]
                )
        
        total_chunks = sum(len(self.text_splitter.split_text(doc['content'])) for doc in documents)
        self.logger.info(f"Ingested {total_chunks} chunks from {len(documents)} documents")
    
    def retrieve_documents(self, query: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Retrieving documents for query: {query}")
        config = self.config.get_retrieval_config()
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search vector database
        results = self.vector_db.query(
            query_embeddings=[query_embedding],
            n_results=config.get('max_results', 5)
        )
        
        if (
            not results
            or not results.get('documents')
            or not results['documents']
            or not results.get('metadatas')
            or not results['metadatas']
            or (results.get('distances') is not None and not results['distances'])
        ):
            return []

        # Format results
        documents = []
        for i in range(len(results['documents'][0])):
            documents.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': (
                    results['distances'][0][i]
                    if (
                        isinstance(results.get('distances'), list)
                        and results['distances']
                        and isinstance(results['distances'][0], list)
                        and results['distances'][0]
                    )
                    else None
                )
            })
        
        self.logger.debug(f"Retrieved {len(documents)} relevant document chunks for query.")
        return documents
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        self.logger.info(f"Generating response for query: {query}")
        # Prepare context
        context = "\n\n".join([doc['content'] for doc in context_docs])
        
        # Create system message with context
        system_message = SystemMessage(content=f"""
        You are a helpful AI assistant. Answer the user's question based on the provided context.
        
        Context:
        {context}
        
        Instructions:
        - Use only the information provided in the context
        - If the answer is not in the context, say so
        - Be concise and accurate
        - Cite relevant parts of the context when possible
        """)
        
        # Create user message
        user_message = HumanMessage(content=query)
        
        # Generate response
        response = self.llm.invoke([system_message, user_message])
        
        self.logger.debug(f"Generated response: {response.content if hasattr(response, 'content') else response}")
        if isinstance(response.content, list):
            return "\n".join(str(x) for x in response.content)
        return response.content
    
    def query(self, question: str) -> Dict[str, Any]:
        self.logger.info(f"Processing query: {question}")
        # Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(question)
        
        # Generate response
        response = self.generate_response(question, retrieved_docs)
        
        # Prepare result
        result = {
            'question': question,
            'response': response,
            'retrieved_documents': retrieved_docs,
            'num_sources': len(retrieved_docs)
        }
        
        self.logger.info(f"Query processed. Response: {response}")
        return result
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection."""
        collection_info = self.vector_db.get_collection_info()
        stats = {
            'total_documents': collection_info.get('count', 0),
            'collection_name': collection_info.get('name', 'unknown'),
            'provider': collection_info.get('provider', 'unknown')
        }
        # Log stats only to file (not console) - CLI will handle user-friendly display
        self.logger.debug(f"Collection stats retrieved: {stats}")
        return stats
    
    def clear_database(self) -> None:
        """Clear all documents from the vector database."""
        self.logger.info("Starting database clearing operation")
        
        try:
            # Get current count before clearing
            collection_info = self.vector_db.get_collection_info()
            initial_count = collection_info.get('count', 0)
            
            if initial_count == 0:
                self.logger.info("Database is already empty")
                return
            
            # Delete the entire collection and recreate it
            self.vector_db.delete_collection()
            
            # Recreate the vector database
            config = self.config.get_vector_db_config()
            self.vector_db = create_vector_db(config)
            
            self.logger.info(f"Successfully cleared {initial_count} documents from database")
                
        except Exception as e:
            self.logger.error(f"Failed to clear database: {e}")
            raise Exception(f"Failed to clear database: {e}") 