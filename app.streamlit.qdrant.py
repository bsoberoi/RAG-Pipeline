#!/usr/bin/env python3
"""
Streamlit Web Interface for the RAG Pipeline with Qdrant.
Optimized for Streamlit Cloud deployment with Qdrant Cloud.
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
    """Streamlit web interface for the RAG Pipeline application with Qdrant."""
    
    def __init__(self):
        """Initialize the Streamlit application."""
        self.setup_page_config()
        self.initialize_session_state()
        self.suppress_console_logging()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="🧠 RAG Pipeline - Qdrant",
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
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    def initialize_rag_pipeline(self, config_path: Optional[str] = None):
        """Initialize the full RAG pipeline with caching."""
        try:
            if config_path is None:
                config_path = "config/config.streamlit.qdrant.yaml"
            
            rag_pipeline = RAGPipeline(config_path)
            st.session_state.rag_pipeline = rag_pipeline
            return rag_pipeline
        except Exception as e:
            st.error(f"❌ Failed to initialize RAG Pipeline: {e}")
            return None
    
    def initialize_vector_db_only(self, config_path: Optional[str] = None):
        """Initialize only the vector database for lightweight operations."""
        try:
            if config_path is None:
                config_path = "config/config.streamlit.qdrant.yaml"
            
            config_loader = ConfigLoader(config_path)
            vector_db_config = config_loader.get_vector_db_config()
            
            # Initialize vector database using factory
            vector_db = create_vector_db(vector_db_config)
            st.session_state.vector_db = vector_db
            return vector_db
        except Exception as e:
            st.error(f"❌ Failed to initialize Vector Database: {e}")
            return None
    
    def get_database_stats(self) -> Optional[Dict[str, Any]]:
        """Get database statistics."""
        try:
            if st.session_state.vector_db_initialized and st.session_state.vector_db:
                return st.session_state.vector_db.get_collection_info()
            elif st.session_state.pipeline_initialized and st.session_state.rag_pipeline:
                return st.session_state.rag_pipeline.get_collection_stats()
            else:
                st.warning("❌ Database not initialized")
                return None
        except Exception as e:
            st.error(f"❌ Error getting database stats: {e}")
            return None
    
    def render_sidebar(self):
        """Render the sidebar navigation."""
        st.sidebar.title("🧠 RAG Pipeline")
        st.sidebar.markdown(f"**Version:** {version_info['version']}")
        
        # System Status
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 System Status")
        
        if st.session_state.pipeline_initialized:
            st.sidebar.success("**🚀 RAG Pipeline**\n\nFully Initialized")
        elif st.session_state.vector_db_initialized:
            st.sidebar.info("**🔍 Vector DB**\n\nDatabase Only")
        else:
            st.sidebar.warning("⚠️ Not Initialized")
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.subheader("🧭 Navigation")
        
        pages = {
            "🏠 Dashboard": "dashboard",
            "🚀 Initialize": "initialize", 
            "📚 Ingest Documents": "ingest",
            "💬 Chat Interface": "chat",
            "🔍 Single Query": "query",
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
        st.markdown("### Welcome to the Retrieval-Augmented Generation System with Qdrant")
        
        # System Overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.pipeline_initialized:
                st.success("**🚀 RAG Pipeline**\n\nFully Initialized")
            else:
                st.error("**🚀 RAG Pipeline**\n\nNot Initialized")
        
        with col2:
            if st.session_state.vector_db_initialized:
                st.success("**🔍 Vector Database**\n\nConnected")
            else:
                st.warning("**🔍 Vector Database**\n\nNot Connected")
        
        with col3:
            # Check GROQ API key
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                st.success("**🤖 GROQ API**\n\nConfigured")
            else:
                st.error("**🤖 GROQ API**\n\nNot Configured")
        
        # Quick Actions
        st.markdown("---")
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
        stats = self.get_database_stats()
        if stats and stats.get('total_documents', 0) > 0:
            st.markdown("---")
            st.subheader("📈 System Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Documents", stats.get('total_documents', 0))
            with col2:
                st.metric("Collection Name", stats.get('collection_name', 'N/A'))
            with col3:
                st.metric("Provider", stats.get('provider', 'N/A'))
            with col4:
                st.metric("Vector Size", stats.get('vector_size', 'N/A'))
        else:
            st.info("💡 No documents found. Use the 'Ingest Documents' page to add content.")
    
    def render_initialize_page(self):
        """Render the initialization page."""
        st.title("🚀 Initialize RAG Pipeline")
        st.markdown("Initialize the system components for document processing and querying with Qdrant.")
        
        # Configuration Info
        st.subheader("📋 Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Vector Database:** Qdrant Cloud")
            st.info("**LLM Provider:** GROQ")
            st.info("**Embedding Model:** sentence-transformers/all-MiniLM-L6-v2")
        
        with col2:
            # Check environment variables
            groq_key = os.getenv('GROQ_API_KEY')
            qdrant_key = os.getenv('QDRANT_API_KEY')
            
            if groq_key:
                st.success("✅ GROQ_API_KEY: Set")
            else:
                st.error("❌ GROQ_API_KEY: Not set")
            
            if qdrant_key:
                st.success("✅ QDRANT_API_KEY: Set")
            else:
                st.warning("⚠️ QDRANT_API_KEY: Not set (using public endpoint)")
        
        # Configuration File Selection
        st.subheader("⚙️ Configuration")
        config_file = st.selectbox(
            "Select Configuration File",
            ["config/config.streamlit.qdrant.yaml"],
            help="Choose the configuration file for initialization"
        )
        
        # Initialize Button
        if st.button("🚀 Initialize RAG Pipeline", type="primary", use_container_width=True):
            with st.spinner("Initializing RAG Pipeline..."):
                try:
                    # Initialize pipeline
                    rag_pipeline = self.initialize_rag_pipeline(config_file if config_file != "config/config.yaml" else None)
                    
                    if rag_pipeline:
                        st.session_state.pipeline_initialized = True
                        st.success("✅ RAG Pipeline initialized successfully!")
                        
                        # Show collection info
                        stats = rag_pipeline.get_collection_stats()
                        if stats:
                            st.info(f"📊 Collection: {stats.get('collection_name', 'N/A')} ({stats.get('total_documents', 0)} documents)")
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to initialize RAG Pipeline")
                        
                except Exception as e:
                    st.error(f"❌ Initialization failed: {e}")
        
        # Status Check
        if st.session_state.pipeline_initialized:
            st.success("✅ RAG Pipeline is already initialized and ready to use!")
    
    def render_ingest_page(self):
        """Render the document ingestion page."""
        st.title("📚 Document Ingestion")
        st.markdown("Upload and process documents to add them to your knowledge base.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # File Upload
        st.subheader("📁 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['txt', 'pdf', 'docx', 'json'],
            accept_multiple_files=True,
            help="Supported formats: TXT, PDF, DOCX, JSON"
        )
        
        if uploaded_files:
            st.subheader("📋 Upload Summary")
            
            for file in uploaded_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {file.name}")
                with col2:
                    st.write(f"{file.size:,} bytes")
                with col3:
                    st.write(f"{file.type}")
            
            # Process Button
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_files = len(uploaded_files)
                processed_files = 0
                
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Process the file
                        status_text.text(f"Processing {uploaded_file.name}...")
                        st.session_state.rag_pipeline.ingest_document(tmp_file_path)
                        
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
                        
                        processed_files += 1
                        progress_bar.progress(processed_files / total_files)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                
                status_text.text("✅ Processing complete!")
                st.success(f"Successfully processed {processed_files}/{total_files} files!")
                
                # Show updated stats
                stats = st.session_state.rag_pipeline.get_collection_stats()
                if stats:
                    st.info(f"📊 Total documents in collection: {stats.get('total_documents', 0)}")
        
        # Directory Upload (Alternative)
        st.markdown("---")
        st.subheader("📁 Upload Directory")
        
        if st.button("📂 Select Directory", use_container_width=True):
            st.info("💡 Directory upload is not available in Streamlit Cloud. Use file upload instead.")
    
    def render_chat_page(self):
        """Render the chat interface page."""
        st.title("💬 Chat Interface")
        st.markdown("Interactive chat with your document knowledge base.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Retrieve relevant documents
                        results = st.session_state.rag_pipeline.retrieve_documents(prompt)
                        
                        if results:
                            # Generate response using GROQ
                            response = st.session_state.rag_pipeline.generate_response(prompt, results)
                            st.markdown(response)
                            
                            # Add assistant message
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            st.warning("No relevant documents found. Try a different question.")
                            
                    except Exception as e:
                        st.error(f"❌ Error generating response: {e}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    def render_query_page(self):
        """Render the single query page."""
        st.title("🔍 Single Query")
        st.markdown("Ask a single question and get an answer from your knowledge base.")
        
        # Ensure pipeline is initialized
        if not st.session_state.pipeline_initialized:
            st.warning("⚠️ RAG Pipeline not initialized. Please initialize first.")
            if st.button("Go to Initialize", type="primary"):
                st.session_state.current_page = "initialize"
                st.rerun()
            return
        
        # Query input
        query = st.text_area(
            "Enter your question:",
            placeholder="What is the main topic of the documents?",
            height=100
        )
        
        if st.button("🔍 Search", type="primary", use_container_width=True):
            if query:
                with st.spinner("Searching..."):
                    try:
                        # Retrieve documents
                        results = st.session_state.rag_pipeline.retrieve_documents(query)
                        
                        if results:
                            st.subheader("📄 Retrieved Documents")
                            
                            for i, result in enumerate(results):
                                with st.expander(f"Document {i+1} (Score: {result['distance']:.3f})"):
                                    st.write("**Content:**")
                                    st.write(result['content'])
                                    st.write("**Metadata:**")
                                    st.json(result['metadata'])
                            
                            # Generate response
                            st.subheader("🤖 Generated Response")
                            response = st.session_state.rag_pipeline.generate_response(query, results)
                            st.write(response)
                        else:
                            st.warning("No relevant documents found.")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing query: {e}")
            else:
                st.warning("Please enter a question.")
    
    def render_stats_page(self):
        """Render the statistics page."""
        st.title("📊 Database Statistics")
        st.markdown("View statistics about your document collection.")
        
        # Initialize vector DB if needed
        if not st.session_state.vector_db_initialized and not st.session_state.pipeline_initialized:
            with st.spinner("Connecting to database..."):
                vector_db = self.initialize_vector_db_only()
                if vector_db:
                    st.session_state.vector_db_initialized = True
                    st.success("✅ Connected to database")
        
        # Get and display stats
        stats = self.get_database_stats()
        
        if stats:
            st.subheader("📈 Collection Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Documents", stats.get('total_documents', stats.get('count', 0)))
            
            with col2:
                st.metric("Collection Name", stats.get('collection_name', 'N/A'))
            
            with col3:
                st.metric("Provider", stats.get('provider', 'N/A'))
            
            with col4:
                st.metric("Vector Size", stats.get('vector_size', 'N/A'))
            
            # Additional info
            if stats.get('metadata'):
                st.subheader("🔧 Configuration")
                st.json(stats['metadata'])
        else:
            st.info("💡 No documents found. Use the 'Ingest Documents' page to add content.")
    
    def render_clear_page(self):
        """Render the database clearing page."""
        st.title("🗑️ Clear Database")
        st.markdown("⚠️ **Warning:** This will permanently delete all documents from your database.")
        
        # Initialize vector DB if needed
        if not st.session_state.vector_db_initialized and not st.session_state.pipeline_initialized:
            with st.spinner("Connecting to database..."):
                vector_db = self.initialize_vector_db_only()
                if vector_db:
                    st.session_state.vector_db_initialized = True
                    st.success("✅ Connected to database")
        
        # Get current stats
        stats = self.get_database_stats()
        if stats:
            st.subheader("📊 Current Database Status")
            st.info(f"**Collection:** {stats.get('collection_name', 'N/A')}")
            st.info(f"**Documents:** {stats.get('total_documents', stats.get('count', 0))}")
            st.info(f"**Provider:** {stats.get('provider', 'N/A')}")
            
            # Clear button
            st.markdown("---")
            st.subheader("⚠️ Clear Database")
            
            if st.button("🗑️ Clear All Documents", type="secondary", use_container_width=True):
                with st.spinner("Clearing database..."):
                    try:
                        if st.session_state.pipeline_initialized:
                            st.session_state.rag_pipeline.clear_database()
                        elif st.session_state.vector_db_initialized:
                            st.session_state.vector_db.delete_collection()
                        
                        st.success("✅ Database cleared successfully!")
                        st.session_state.pipeline_initialized = False
                        st.session_state.vector_db_initialized = False
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error clearing database: {e}")
        else:
            st.info("💡 Database is already empty or not connected.")
    
    def render_logs_page(self):
        """Render the log management page."""
        st.title("📝 Log Management")
        st.markdown("View and manage application logs.")
        
        # Log level selection
        st.subheader("📊 Log Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Current Log Level:** {log_level}")
        
        with col2:
            st.info(f"**Log Path:** ./logs")
        
        # Recent logs
        st.subheader("📋 Recent Logs")
        
        log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
        
        if log_files:
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            selected_log = st.selectbox(
                "Select log file:",
                [f.name for f in log_files],
                help="Choose a log file to view"
            )
            
            if selected_log:
                log_path = Path("logs") / selected_log
                
                # Show log file info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{log_path.stat().st_size:,} bytes")
                with col2:
                    st.metric("Last Modified", time.ctime(log_path.stat().st_mtime))
                with col3:
                    st.metric("Lines", sum(1 for _ in open(log_path, 'r', encoding='utf-8')))
                
                # Display log content
                st.subheader("📄 Log Content")
                
                # Show last N lines
                num_lines = st.slider("Number of lines to show:", 10, 1000, 100)
                
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-num_lines:]
                        
                    log_content = ''.join(recent_lines)
                    st.code(log_content, language='text')
                    
                except Exception as e:
                    st.error(f"❌ Error reading log file: {e}")
        else:
            st.info("💡 No log files found in the logs directory.")
    
    def render_info_page(self):
        """Render the system information page."""
        st.title("📋 System Information")
        st.markdown("Detailed information about your RAG Pipeline system.")
        
        # Version Information
        st.subheader("🔢 Version Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Version", version_info['version'])
        
        with col2:
            st.metric("Major", version_info['major'])
        
        with col3:
            st.metric("Minor", version_info['minor'])
        
        # System Configuration
        st.subheader("⚙️ System Configuration")
        
        config_info = {
            "Vector Database": "Qdrant Cloud",
            "LLM Provider": "GROQ",
            "Embedding Model": "sentence-transformers/all-MiniLM-L6-v2",
            "Python Version": sys.version.split()[0],
            "Streamlit Version": st.__version__,
            "Platform": sys.platform
        }
        
        for key, value in config_info.items():
            st.info(f"**{key}:** {value}")
        
        # Environment Variables
        st.subheader("🔐 Environment Variables")
        
        env_vars = {
            "GROQ_API_KEY": "Set" if os.getenv('GROQ_API_KEY') else "Not Set",
            "QDRANT_API_KEY": "Set" if os.getenv('QDRANT_API_KEY') else "Not Set",
        }
        
        for key, value in env_vars.items():
            if value == "Set":
                st.success(f"✅ **{key}:** {value}")
            else:
                st.warning(f"⚠️ **{key}:** {value}")
        
        # Database Status
        st.subheader("🗄️ Database Status")
        
        stats = self.get_database_stats()
        if stats:
            st.success("✅ Database Connected")
            st.json(stats)
        else:
            st.warning("⚠️ Database Not Connected")
    
    def render_stop_page(self):
        """Render the application stop page."""
        st.title("🛑 Stop Application")
        st.markdown("Stop the RAG Pipeline application.")
        
        # Confirmation
        st.warning("⚠️ **Warning:** This will stop the application and clear all session data.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🛑 Stop Application", type="secondary", use_container_width=True):
                st.session_state.pipeline_initialized = False
                st.session_state.vector_db_initialized = False
                st.session_state.rag_pipeline = None
                st.session_state.vector_db = None
                st.session_state.chat_history = []
                st.session_state.messages = []
                
                st.success("✅ Application stopped successfully!")
                st.info("💡 Refresh the page to restart the application.")
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
            self.render_chat_page()
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
    """Main function to run the Streamlit app."""
    app = RAGStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()

