#!/usr/bin/env python3
"""
Streamlit Web Interface for the RAG Pipeline.
Provides a comprehensive web-based interface for document ingestion, querying, and management.
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st
import logging

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.init_manager import init_logging_and_config
from src.utils.version_manager import VersionManager

# Initialize logging and config
@st.cache_resource
def initialize_logging():
    """Initialize logging configuration once."""
    return init_logging_and_config()

config, log_level = initialize_logging()

# Initialize version manager
@st.cache_resource
def get_version_info():
    """Get version information."""
    try:
        vm = VersionManager()
        return vm.get_version_info()
    except Exception as e:
        return {'version': 'unknown', 'major': '0', 'minor': '0', 'patch': '0'}

version_info = get_version_info()

from src.rag_pipeline import RAGPipeline
from src.utils.config_loader import ConfigLoader
from src.vector_db import create_vector_db


class RAGStreamlitApp:
    """Streamlit web interface for the RAG Pipeline application."""
    
    def __init__(self):
        """Initialize the Streamlit application."""
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="🧠 RAG Pipeline",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'rag_pipeline' not in st.session_state:
            st.session_state.rag_pipeline = None
        if 'vector_db' not in st.session_state:
            st.session_state.vector_db = None
        if 'pipeline_initialized' not in st.session_state:
            st.session_state.pipeline_initialized = False
        if 'vector_db_initialized' not in st.session_state:
            st.session_state.vector_db_initialized = False
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def suppress_console_logging(self):
        """Temporarily suppress console logging for cleaner UI."""
        root_logger = logging.getLogger()
        
        # Store original handlers if not already stored
        if not hasattr(st.session_state, '_original_handlers'):
            st.session_state._original_handlers = root_logger.handlers.copy()
        
        # Remove StreamHandlers (console output), keep FileHandlers
        for handler in root_logger.handlers.copy():
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
    
    def restore_console_logging(self):
        """Restore console logging after operations."""
        if hasattr(st.session_state, '_original_handlers'):
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.handlers.extend(st.session_state._original_handlers)
    
    @st.cache_resource
    def initialize_rag_pipeline(_self, config_path: Optional[str] = None):
        """Initialize the full RAG pipeline with caching."""
        try:
            if config_path:
                return RAGPipeline(config_path)
            else:
                return RAGPipeline()
        except Exception as e:
            st.error(f"❌ Failed to initialize RAG Pipeline: {e}")
            st.error("💡 Make sure all dependencies are installed and GROQ_API_KEY is set")
            return None
    
    def initialize_vector_db_only(self, config_path: Optional[str] = None):
        """Initialize only the vector database for lightweight operations."""
        try:
            # Load config
            if not config_path:
                config_path = os.path.join(os.getcwd(), "config", "config.yaml")
            
            config = ConfigLoader(config_path)
            vector_db_config = config.get_vector_db_config()
            
            # Initialize vector database using factory
            vector_db = create_vector_db(vector_db_config)
            
            return vector_db
            
        except Exception as e:
            st.error(f"❌ Failed to connect to vector database: {e}")
            return None
    
    def get_database_stats(self):
        """Get database statistics using available connection."""
        try:
            if st.session_state.rag_pipeline:
                return st.session_state.rag_pipeline.get_collection_stats()
            elif st.session_state.vector_db:
                collection_info = st.session_state.vector_db.get_collection_info()
                return {
                    'total_documents': collection_info.get('count', 0),
                    'collection_name': collection_info.get('name', 'unknown'),
                    'provider': collection_info.get('provider', 'unknown')
                }
            else:
                return None
        except Exception as e:
            st.error(f"❌ Error getting database stats: {e}")
            return None
    
    def get_log_files(self):
        """Get all log files sorted by modification time (newest first)."""
        try:
            logs_path = Path("./logs")
            if not logs_path.exists():
                return []
            
            log_files = []
            for log_file in logs_path.glob("*.log"):
                try:
                    stat = log_file.stat()
                    log_files.append({
                        'name': log_file.name,
                        'path': str(log_file),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'modified_str': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                    })
                except Exception:
                    continue
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            return log_files
            
        except Exception as e:
            st.error(f"❌ Error getting log files: {e}")
            return []
    
    def cleanup_old_logs(self, keep_count=5):
        """Delete old log files, keeping only the latest 'keep_count' files."""
        try:
            log_files = self.get_log_files()
            
            if len(log_files) <= keep_count:
                return 0, []
            
            # Files to delete (all except the first 'keep_count')
            files_to_delete = log_files[keep_count:]
            deleted_files = []
            
            for file_info in files_to_delete:
                try:
                    Path(file_info['path']).unlink()
                    deleted_files.append(file_info['name'])
                except Exception as e:
                    st.error(f"❌ Failed to delete {file_info['name']}: {e}")
            
            return len(deleted_files), deleted_files
            
        except Exception as e:
            st.error(f"❌ Error during log cleanup: {e}")
            return 0, []
    
    def display_stats(self):
        """Display database statistics."""
        stats = self.get_database_stats()
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Documents", stats['total_documents'])
            with col2:
                st.metric("Collection Name", stats['collection_name'])
            
            if stats['total_documents'] == 0:
                st.info("💡 No documents found. Use the 'Ingest Documents' tab to add documents.")
        else:
            st.warning("❌ Database not initialized")
    
    def render_sidebar(self):
        """Render the sidebar navigation."""
        st.sidebar.title("🧠 RAG Pipeline")
        
        # Version information
        st.sidebar.caption(f"Version {version_info['version']}")
        st.sidebar.markdown("---")
        
        # Pipeline Status
        st.sidebar.subheader("🔧 System Status")
        
        if st.session_state.pipeline_initialized:
            st.sidebar.success("✅ RAG Pipeline Ready")
        elif st.session_state.vector_db_initialized:
            st.sidebar.info("🔍 Vector DB Connected")
        else:
            st.sidebar.warning("⚠️ Not Initialized")
        
        # Quick Stats
        stats = self.get_database_stats()
        if stats:
            st.sidebar.metric("Documents", stats['total_documents'])
        
        st.sidebar.markdown("---")
        
        # Navigation
        pages = {
            "🏠 Dashboard": "dashboard",
            "🚀 Initialize": "initialize", 
            "📚 Ingest Documents": "ingest",
            "💬 Chat Interface": "chat",
            "❓ Single Query": "query",
            "📊 Statistics": "stats",
            "🗑️ Clear Database": "clear",
            "📝 Log Management": "logs",
            "📋 System Info": "info",
            "🛑 Stop App": "stop"
        }
        
        selected_page = st.sidebar.radio("Navigate", list(pages.keys()))
        # Update session state when page changes
        if pages[selected_page] != st.session_state.current_page:
            st.session_state.current_page = pages[selected_page]
        return st.session_state.current_page
    
    def render_dashboard(self):
        """Render the main dashboard."""
        st.title("🧠 RAG Pipeline Dashboard")
        st.markdown("### Welcome to the Retrieval-Augmented Generation System")
        
        # System Status Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.pipeline_initialized:
                st.success("**🚀 RAG Pipeline**\n\nFully Initialized")
            else:
                st.error("**🚀 RAG Pipeline**\n\nNot Initialized")
        
        with col2:
            stats = self.get_database_stats()
            if stats:
                st.info(f"**📊 Database**\n\n{stats['total_documents']} Documents")
            else:
                st.warning("**📊 Database**\n\nNot Connected")
        
        with col3:
            if os.path.exists("./data/raw") and any(Path("./data/raw").iterdir()):
                st.info("**📁 Raw Data**\n\nFiles Available")
            else:
                st.warning("**📁 Raw Data**\n\nNo Files Found")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("🎯 Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 Initialize System", use_container_width=True):
                st.session_state.current_page = "initialize"
                st.rerun()
        
        with col2:
            if st.button("📚 Ingest Documents", use_container_width=True):
                st.session_state.current_page = "ingest"
                st.rerun()
        
        with col3:
            if st.button("💬 Start Chatting", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        
        with col4:
            if st.button("📊 View Statistics", use_container_width=True):
                st.session_state.current_page = "stats"
                st.rerun()
        
        # Recent Activity or Statistics
        if stats and stats['total_documents'] > 0:
            st.markdown("---")
            st.subheader("📈 System Overview")
            self.display_stats()
    
    def render_initialize_page(self):
        """Render the initialization page."""
        st.title("🚀 Initialize RAG Pipeline")
        st.markdown("Initialize the system components for document processing and querying.")
        
        # Configuration
        st.subheader("⚙️ Configuration")
        config_file = st.text_input("Config File Path", value="config/config.yaml")
        
        col1, col2 = st.columns(2)
        with col1:
            skip_test = st.checkbox("Skip test query after initialization")
        with col2:
            auto_ingest = st.checkbox("Auto-ingest documents from data/raw", value=True)
        
        st.markdown("---")
        
        # Initialize Button
        if st.button("🚀 Initialize RAG Pipeline", type="primary", use_container_width=True):
            with st.spinner("Initializing RAG Pipeline..."):
                # Suppress logging for cleaner UI
                self.suppress_console_logging()
                
                try:
                    # Initialize pipeline
                    rag_pipeline = self.initialize_rag_pipeline(config_file if config_file != "config/config.yaml" else None)
                    
                    if rag_pipeline:
                        st.session_state.rag_pipeline = rag_pipeline
                        st.session_state.pipeline_initialized = True
                        st.success("✅ RAG Pipeline initialized successfully!")
                        
                        # Display initial stats
                        st.subheader("📊 Initial Statistics")
                        self.display_stats()
                        
                        # Check for documents in default location
                        raw_data_path = Path("data/raw")
                        if raw_data_path.exists() and any(raw_data_path.iterdir()) and auto_ingest:
                            st.info(f"📁 Found documents in {raw_data_path}")
                            
                            if st.button("📚 Ingest Found Documents", type="secondary"):
                                with st.spinner("Ingesting documents..."):
                                    try:
                                        st.session_state.rag_pipeline.ingest_directory(str(raw_data_path))
                                        st.success("✅ Documents ingested successfully!")
                                        
                                        # Update stats
                                        st.subheader("📊 Updated Statistics")
                                        self.display_stats()
                                    except Exception as e:
                                        st.error(f"❌ Ingestion failed: {e}")
                        
                        # Run test query if enabled
                        if not skip_test and st.session_state.rag_pipeline.get_collection_stats()['total_documents'] > 0:
                            st.subheader("🔍 Test Query")
                            with st.spinner("Running test query..."):
                                try:
                                    result = st.session_state.rag_pipeline.query("What is the main topic discussed in the documents?")
                                    
                                    st.success("✅ Test query completed!")
                                    st.write("**Question:**", result['question'])
                                    st.write("**Response:**", result['response'])
                                    st.write("**Sources used:**", result['num_sources'])
                                except Exception as e:
                                    st.error(f"❌ Test query failed: {e}")
                    
                finally:
                    self.restore_console_logging()
        
        # Status Display
        if st.session_state.pipeline_initialized:
            st.success("✅ RAG Pipeline is already initialized and ready to use!")
    
    def render_ingest_page(self):
        """Render the document ingestion page."""
        st.title("📚 Ingest Documents")
        st.markdown("Upload documents or specify directories to add to the knowledge base.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # Ingestion Options
        ingest_method = st.radio(
            "Choose ingestion method:",
            ["📄 Upload Files", "📁 Directory Path", "🔄 Re-ingest data/raw"],
            horizontal=True
        )
        
        if ingest_method == "📄 Upload Files":
            st.subheader("📄 Upload Files")
            uploaded_files = st.file_uploader(
                "Choose files to upload",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt', 'json']
            )
            
            if uploaded_files and st.button("📚 Ingest Uploaded Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                self.suppress_console_logging()
                try:
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            st.session_state.rag_pipeline.ingest_document(tmp_file_path)
                        finally:
                            os.unlink(tmp_file_path)  # Clean up temp file
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.text("✅ All files processed successfully!")
                    st.success(f"✅ Ingested {len(uploaded_files)} files successfully!")
                    
                    # Show updated stats
                    st.subheader("📊 Updated Statistics")
                    self.display_stats()
                    
                except Exception as e:
                    st.error(f"❌ Ingestion failed: {e}")
                finally:
                    self.restore_console_logging()
        
        elif ingest_method == "📁 Directory Path":
            st.subheader("📁 Directory Path")
            directory_path = st.text_input("Enter directory path:", placeholder="./data/documents")
            recursive = st.checkbox("Search subdirectories recursively")
            
            if directory_path and st.button("📚 Ingest Directory", type="primary"):
                path = Path(directory_path)
                if not path.exists():
                    st.error(f"❌ Directory not found: {directory_path}")
                else:
                    with st.spinner(f"Ingesting documents from {path}..."):
                        self.suppress_console_logging()
                        try:
                            start_time = time.time()
                            st.session_state.rag_pipeline.ingest_directory(str(path))
                            elapsed = time.time() - start_time
                            
                            st.success(f"✅ Ingestion completed in {elapsed:.2f} seconds")
                            
                            # Show updated stats
                            st.subheader("📊 Updated Statistics")
                            self.display_stats()
                            
                        except Exception as e:
                            st.error(f"❌ Ingestion failed: {e}")
                        finally:
                            self.restore_console_logging()
        
        elif ingest_method == "🔄 Re-ingest data/raw":
            st.subheader("🔄 Re-ingest Default Directory")
            raw_data_path = Path("data/raw")
            
            if raw_data_path.exists() and any(raw_data_path.iterdir()):
                st.info(f"📁 Found documents in {raw_data_path}")
                
                if st.button("📚 Ingest data/raw Directory", type="primary"):
                    with st.spinner("Ingesting documents from data/raw..."):
                        self.suppress_console_logging()
                        try:
                            start_time = time.time()
                            st.session_state.rag_pipeline.ingest_directory(str(raw_data_path))
                            elapsed = time.time() - start_time
                            
                            st.success(f"✅ Ingestion completed in {elapsed:.2f} seconds")
                            
                            # Show updated stats
                            st.subheader("📊 Updated Statistics")
                            self.display_stats()
                            
                        except Exception as e:
                            st.error(f"❌ Ingestion failed: {e}")
                        finally:
                            self.restore_console_logging()
            else:
                st.warning("⚠️ No documents found in data/raw directory")
    
    def render_chat_interface(self):
        """Render the interactive chat interface."""
        st.title("💬 Interactive Chat")
        st.markdown("Chat with your documents using natural language queries.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # Check if documents are available
        stats = self.get_database_stats()
        if not stats or stats['total_documents'] == 0:
            st.warning("❌ No documents in database. Please ingest documents first.")
            if st.button("Go to Ingest Documents", type="primary"):
                st.session_state.current_page = "ingest"
                st.rerun()
            return
        
        # Chat Interface
        st.subheader(f"💬 Chat Interface ({stats['total_documents']} documents available)")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "sources" in message:
                    st.caption(f"📚 {message['sources']} sources used")
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching through documents..."):
                    self.suppress_console_logging()
                    try:
                        result = st.session_state.rag_pipeline.query(prompt)
                        
                        st.markdown(result['response'])
                        st.caption(f"📚 {result['num_sources']} sources used")
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": result['response'],
                            "sources": result['num_sources']
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Error processing query: {e}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                    finally:
                        self.restore_console_logging()
        
        # Chat controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("📊 Show Statistics"):
                self.display_stats()
        
        with col3:
            if st.button("💾 Export Chat", help="Feature coming soon"):
                st.info("💡 Chat export feature coming soon!")
    
    def render_query_page(self):
        """Render the single query page."""
        st.title("❓ Single Query")
        st.markdown("Ask a single question and get a detailed response.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # Check if documents are available
        stats = self.get_database_stats()
        if not stats or stats['total_documents'] == 0:
            st.warning("❌ No documents in database. Please ingest documents first.")
            if st.button("Go to Ingest Documents", type="primary"):
                st.session_state.current_page = "ingest"
                st.rerun()
            return
        
        st.subheader(f"❓ Ask Your Question ({stats['total_documents']} documents available)")
        
        # Query input
        question = st.text_area("Enter your question:", placeholder="What is the main topic discussed in the documents?", height=100)
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            max_results = st.slider("Maximum source documents to retrieve", 1, 20, 5)
            show_sources = st.checkbox("Show detailed source information", value=True)
        
        # Query button
        if st.button("🔍 Search", type="primary", disabled=not question.strip()):
            with st.spinner("🔍 Searching through documents..."):
                self.suppress_console_logging()
                try:
                    result = st.session_state.rag_pipeline.query(question.strip())
                    
                    # Display results
                    st.success("✅ Query completed!")
                    
                    st.subheader("💬 Response")
                    st.write(result['response'])
                    
                    st.subheader("📊 Query Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sources Used", result['num_sources'])
                    with col2:
                        st.metric("Query Length", len(question.strip()))
                    
                    # Show source details if enabled
                    if show_sources and result['retrieved_documents']:
                        st.subheader("📄 Source Documents")
                        for i, doc in enumerate(result['retrieved_documents'][:3], 1):
                            with st.expander(f"Source {i}: {doc['metadata'].get('filename', 'Unknown')}"):
                                st.write("**Content Preview:**")
                                st.write(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
                                
                                if 'distance' in doc and doc['distance'] is not None:
                                    relevance = 1 - doc['distance']
                                    st.metric("Relevance Score", f"{relevance:.3f}")
                                
                                st.json(doc['metadata'])
                    
                except Exception as e:
                    st.error(f"❌ Query failed: {e}")
                finally:
                    self.restore_console_logging()
    
    def render_stats_page(self):
        """Render the statistics page."""
        st.title("📊 Database Statistics")
        st.markdown("View detailed information about your document database.")
        
        # Initialize vector DB if needed
        if not st.session_state.vector_db_initialized and not st.session_state.pipeline_initialized:
            with st.spinner("🔍 Connecting to vector database..."):
                vector_db = self.initialize_vector_db_only()
                if vector_db:
                    st.session_state.vector_db = vector_db
                    st.session_state.vector_db_initialized = True
        
        # Display statistics
        stats = self.get_database_stats()
        if stats:
            # Main metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📚 Total Documents", stats['total_documents'])
            
            with col2:
                st.metric("🗂️ Collection Name", stats['collection_name'])
            
            with col3:
                # Calculate average documents per day (placeholder)
                st.metric("📈 Status", "Active" if stats['total_documents'] > 0 else "Empty")
            
            # Additional information
            st.markdown("---")
            
            if stats['total_documents'] > 0:
                st.success("✅ Database is ready for queries!")
                
                # File system information
                st.subheader("💾 Storage Information")
                
                vector_db_path = "./data/vectors"
                if os.path.exists(vector_db_path):
                    try:
                        # Calculate directory size
                        total_size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(vector_db_path)
                            for filename in filenames
                        )
                        size_mb = total_size / (1024 * 1024)
                        st.metric("Database Size", f"{size_mb:.2f} MB")
                    except Exception:
                        st.metric("Database Size", "Unable to calculate")
                
                # Log directory information
                logs_path = "./logs"
                if os.path.exists(logs_path):
                    log_files = list(Path(logs_path).glob("*.log"))
                    st.metric("Log Files", len(log_files))
            else:
                st.info("💡 No documents found. Use the 'Ingest Documents' page to add content.")
        else:
            st.error("❌ Unable to connect to database. Please check your configuration.")
        
        # Refresh button
        if st.button("🔄 Refresh Statistics", type="secondary"):
            st.rerun()
    
    def render_clear_page(self):
        """Render the database clearing page."""
        st.title("🗑️ Clear Database")
        st.markdown("Remove all documents from the knowledge base.")
        
        # Initialize vector DB if needed
        if not st.session_state.vector_db_initialized and not st.session_state.pipeline_initialized:
            with st.spinner("🔍 Connecting to vector database..."):
                vector_db = self.initialize_vector_db_only()
                if vector_db:
                    st.session_state.vector_db = vector_db
                    st.session_state.vector_db_initialized = True
        
        # Get current stats
        stats = self.get_database_stats()
        
        if not stats:
            st.error("❌ Unable to connect to database. Please check your configuration.")
            return
        
        if stats['total_documents'] == 0:
            st.info("📭 Database is already empty.")
            return
        
        # Warning and confirmation
        st.warning(f"⚠️ This will permanently delete **{stats['total_documents']} documents** from the database.")
        st.error("🚨 This action cannot be undone!")
        
        # Confirmation steps
        st.subheader("🔐 Confirmation Required")
        
        confirm_text = st.text_input(
            "Type 'DELETE' to confirm:",
            placeholder="DELETE"
        )
        
        confirm_checkbox = st.checkbox(
            f"I understand that this will delete {stats['total_documents']} documents permanently"
        )
        
        # Clear button
        if st.button(
            f"🗑️ Clear Database ({stats['total_documents']} documents)",
            type="primary",
            disabled=confirm_text != "DELETE" or not confirm_checkbox
        ):
            with st.spinner("🗑️ Clearing database..."):
                try:
                    initial_count = stats['total_documents']
                    
                    # Clear database using vector DB
                    if st.session_state.vector_db:
                        vector_db = st.session_state.vector_db
                    elif st.session_state.rag_pipeline:
                        vector_db = st.session_state.rag_pipeline.vector_db
                    else:
                        st.error("❌ No database connection available")
                        return
                    
                    # Get all document IDs
                    results = vector_db.get(include=[])  # Get only metadata and IDs
                    
                    if results and results.get('ids') and len(results['ids']) > 0:
                        # Delete all documents by their IDs
                        vector_db.delete(ids=results['ids'])
                        st.success(f"✅ Database cleared successfully! Removed {initial_count} documents.")
                    else:
                        st.success("✅ Database cleared successfully! No documents found to remove.")
                    
                    # Reset session state
                    if 'chat_history' in st.session_state:
                        st.session_state.chat_history = []
                    
                    # Show updated stats
                    st.subheader("📊 Updated Statistics")
                    self.display_stats()
                    
                except Exception as e:
                    st.error(f"❌ Failed to clear database: {e}")
    
    def render_logs_page(self):
        """Render the log management page."""
        st.title("📝 Log Management")
        st.markdown("Browse and manage system log files.")
        
        # Get log files
        log_files = self.get_log_files()
        
        if not log_files:
            st.info("📭 No log files found.")
            return
        
        # Log statistics
        st.subheader("📊 Log Statistics")
        
        total_size = sum(f['size'] for f in log_files)
        total_size_mb = total_size / (1024 * 1024)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Files", len(log_files))
        with col2:
            st.metric("Total Size", f"{total_size_mb:.2f} MB")
        with col3:
            st.metric("Oldest File", log_files[-1]['modified_str'] if log_files else "N/A")
        with col4:
            st.metric("Newest File", log_files[0]['modified_str'] if log_files else "N/A")
        
        st.markdown("---")
        
        # Log file list and actions
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Log Files")
            
            # Create DataFrame for log files
            import pandas as pd
            log_data = []
            for f in log_files:
                log_data.append({
                    "File Name": f['name'],
                    "Size (KB)": f"{f['size'] / 1024:.1f}",
                    "Modified": f['modified_str']
                })
            
            df = pd.DataFrame(log_data)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            st.subheader("🔧 Actions")
            
            # Cleanup options
            keep_count = st.number_input("Keep latest files", min_value=1, max_value=20, value=5)
            
            if len(log_files) > keep_count:
                files_to_delete = len(log_files) - keep_count
                st.warning(f"⚠️ This will delete {files_to_delete} old log files")
                
                if st.button("🗑️ Clean Up Old Logs", type="primary"):
                    deleted_count, deleted_files = self.cleanup_old_logs(keep_count)
                    if deleted_count > 0:
                        st.success(f"✅ Deleted {deleted_count} old log files!")
                        st.write("**Deleted files:**")
                        for file_name in deleted_files:
                            st.write(f"- {file_name}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("ℹ️ No files were deleted.")
            else:
                st.info(f"✅ Only {len(log_files)} files found. No cleanup needed.")
            
            # Refresh button
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # Log file viewer
        st.subheader("👁️ Log File Viewer")
        
        if log_files:
            # File selection
            selected_file = st.selectbox(
                "Select a log file to view:",
                options=[f['name'] for f in log_files],
                format_func=lambda x: f"{x} ({next(f['modified_str'] for f in log_files if f['name'] == x)})"
            )
            
            if selected_file:
                selected_file_info = next(f for f in log_files if f['name'] == selected_file)
                
                # File information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{selected_file_info['size']} bytes")
                with col2:
                    st.metric("Size (KB)", f"{selected_file_info['size'] / 1024:.1f} KB")
                with col3:
                    st.metric("Modified", selected_file_info['modified_str'])
                
                # Display options
                col1, col2 = st.columns(2)
                with col1:
                    show_lines = st.number_input("Number of lines to show", min_value=10, max_value=1000, value=100)
                with col2:
                    from_end = st.checkbox("Show from end (tail)", value=True)
                
                # Read and display file content
                try:
                    with open(selected_file_info['path'], 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    if from_end:
                        display_lines = lines[-show_lines:] if len(lines) > show_lines else lines
                        st.info(f"📄 Showing last {len(display_lines)} lines of {len(lines)} total lines")
                    else:
                        display_lines = lines[:show_lines] if len(lines) > show_lines else lines
                        st.info(f"📄 Showing first {len(display_lines)} lines of {len(lines)} total lines")
                    
                    # Display content in a text area
                    content = ''.join(display_lines)
                    st.text_area("Log Content", content, height=400, key=f"log_content_{selected_file}")
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Full Log File",
                        data=''.join(lines),
                        file_name=selected_file,
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error reading log file: {e}")
    
    def render_info_page(self):
        """Render the system information page."""
        st.title("📋 System Information")
        st.markdown("View system configuration and supported formats.")
        
        # Supported file formats
        st.subheader("🔧 Supported File Formats")
        formats = [
            {"Format": "PDF", "Extension": ".pdf", "Description": "Portable Document Format files"},
            {"Format": "Word", "Extension": ".docx", "Description": "Microsoft Word documents"},
            {"Format": "Text", "Extension": ".txt", "Description": "Plain text files"},
            {"Format": "JSON", "Extension": ".json", "Description": "JSON data files"}
        ]
        
        import pandas as pd
        df = pd.DataFrame(formats)
        st.dataframe(df, use_container_width=True)
        
        # Configuration information
        st.subheader("⚙️ Configuration")
        
        config_info = {
            "Config File": "config/config.yaml",
            "Log Directory": "./logs", 
            "Vector Database": "./data/vectors",
            "Raw Documents": "./data/raw"
        }
        
        for key, value in config_info.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{key}:**")
            with col2:
                st.code(value)
        
        # System status
        st.subheader("🔍 System Status")
        
        status_checks = []
        
        # Check config file
        config_exists = os.path.exists("config/config.yaml")
        status_checks.append({
            "Component": "Configuration File",
            "Status": "✅ Found" if config_exists else "❌ Missing",
            "Path": "config/config.yaml"
        })
        
        # Check log directory
        logs_exist = os.path.exists("./logs")
        status_checks.append({
            "Component": "Log Directory", 
            "Status": "✅ Found" if logs_exist else "❌ Missing",
            "Path": "./logs"
        })
        
        # Check vector database
        vectors_exist = os.path.exists("./data/vectors")
        status_checks.append({
            "Component": "Vector Database",
            "Status": "✅ Found" if vectors_exist else "❌ Missing",
            "Path": "./data/vectors"
        })
        
        # Check raw data
        raw_data_exists = os.path.exists("./data/raw")
        status_checks.append({
            "Component": "Raw Data Directory",
            "Status": "✅ Found" if raw_data_exists else "❌ Missing", 
            "Path": "./data/raw"
        })
        
        status_df = pd.DataFrame(status_checks)
        st.dataframe(status_df, use_container_width=True)
        
        # Environment information
        st.subheader("🌍 Environment")
        
        env_info = {
            "Python Version": sys.version.split()[0],
            "Streamlit Version": st.__version__,
            "RAG Pipeline Version": version_info['version'],
            "Working Directory": os.getcwd(),
            "GROQ_API_KEY": "✅ Set" if os.getenv('GROQ_API_KEY') else "❌ Not Set"
        }
        
        for key, value in env_info.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{key}:**")
            with col2:
                if key == "GROQ_API_KEY":
                    if "✅" in value:
                        st.success(value)
                    else:
                        st.error(value)
                else:
                    st.code(value)
    
    def render_stop_page(self):
        """Render the application stop page."""
        st.title("🛑 Stop Application")
        st.markdown("Gracefully shutdown the RAG Pipeline application.")
        
        # Warning message
        st.warning("⚠️ This will stop the current Streamlit session.")
        st.info("💡 To restart the application, run the startup command again.")
        
        # Current session information
        st.subheader("📊 Current Session Info")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pipeline_status = "✅ Active" if st.session_state.pipeline_initialized else "❌ Not Active"
            st.metric("RAG Pipeline", pipeline_status)
        
        with col2:
            db_status = "✅ Connected" if st.session_state.vector_db_initialized else "❌ Not Connected"
            st.metric("Vector Database", db_status)
        
        with col3:
            chat_messages = len(st.session_state.chat_history) if st.session_state.chat_history else 0
            st.metric("Chat Messages", chat_messages)
        
        st.markdown("---")
        
        # Cleanup options
        st.subheader("🧹 Cleanup Options")
        
        clear_chat = st.checkbox("Clear chat history before stopping", value=True)
        clear_cache = st.checkbox("Clear cached resources", value=True)
        
        st.markdown("---")
        
        # Stop button with confirmation
        st.subheader("🔐 Confirmation Required")
        
        confirm_stop = st.checkbox("I understand this will stop the application")
        
        if st.button("🛑 Stop Application", type="primary", disabled=not confirm_stop):
            # Perform cleanup if requested
            if clear_chat and 'chat_history' in st.session_state:
                st.session_state.chat_history = []
                st.success("✅ Chat history cleared")
            
            if clear_cache:
                st.cache_resource.clear()
                st.success("✅ Cache cleared") 
            
            # Display final message
            st.success("✅ Application cleanup completed")
            st.info("🔄 The application will stop now. Restart by running your startup command.")
            
            # Add a small delay to show the message
            time.sleep(2)
            
            # Stop the application
            st.stop()
        
        # Alternative: Return to dashboard
        st.markdown("---")
        if st.button("↩️ Return to Dashboard", type="secondary"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    def run(self):
        """Run the main Streamlit application."""
        # Render sidebar and get selected page
        selected_page = self.render_sidebar()
        
                # Route to appropriate page
        if selected_page == "dashboard":
            self.render_dashboard()
        elif selected_page == "initialize":
            self.render_initialize_page()
        elif selected_page == "ingest":
            self.render_ingest_page()
        elif selected_page == "chat":
            self.render_chat_interface()
        elif selected_page == "query":
            self.render_query_page()
        elif selected_page == "stats":
            self.render_stats_page()
        elif selected_page == "clear":
            self.render_clear_page()
        elif selected_page == "logs":
            self.render_logs_page()
        elif selected_page == "info":
            self.render_info_page()
        elif selected_page == "stop":
            self.render_stop_page()


def main():
    """Entry point for the Streamlit application."""
    try:
        app = RAGStreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        st.error("Please check your configuration and try again.")


if __name__ == "__main__":
    main() 