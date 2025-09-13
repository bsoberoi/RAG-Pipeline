#!/usr/bin/env python3
"""
Streamlit Cloud Compatible RAG Pipeline Application.
This version fixes ChromaDB SQLite compatibility issues on Streamlit Cloud.
"""

# Fix for ChromaDB SQLite compatibility on Streamlit Cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import version info
try:
    from src.utils.version_manager import VersionManager
    vm = VersionManager()
    version_info = vm.get_version_info()
except Exception:
    version_info = {"version": "1.0.1"}

from src.rag_pipeline import RAGPipeline
from src.utils.config_loader import ConfigLoader
from src.vector_db import create_vector_db

# Configure page
st.set_page_config(
    page_title="RAG Pipeline - Streamlit Cloud",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better cloud experience
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .cloud-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-left: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .success-box {
        background-color: #E8F5E8;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitCloudRAGApp:
    """Streamlit Cloud compatible RAG Pipeline application."""
    
    def __init__(self):
        """Initialize the Streamlit Cloud RAG app."""
        self.config_path = "config/config.yaml"
        self._setup_session_state()
    
    def _setup_session_state(self):
        """Initialize session state variables."""
        if 'rag_pipeline' not in st.session_state:
            st.session_state.rag_pipeline = None
        if 'vector_db' not in st.session_state:
            st.session_state.vector_db = None
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'sqlite_fix_applied' not in st.session_state:
            st.session_state.sqlite_fix_applied = True
    
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
                config_path = self.config_path
            
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
    
    def render_header(self):
        """Render the application header."""
        st.markdown(f"""
        <div class="main-header">
            🧠 RAG Pipeline
            <span class="cloud-badge">Streamlit Cloud</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Version info
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.caption(f"Version {version_info.get('version', '1.0.1')} | ChromaDB Compatible")
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Show SQLite fix status
            if st.session_state.sqlite_fix_applied:
                st.markdown("""
                <div class="success-box">
                    <strong>✅ SQLite Fix Applied</strong><br>
                    ChromaDB compatibility enabled for Streamlit Cloud
                </div>
                """, unsafe_allow_html=True)
            
            # Show current config
            st.subheader("Current Settings")
            try:
                config = ConfigLoader(self.config_path)
                vector_config = config.get_vector_db_config()
                
                st.info(f"""
                **Vector DB Provider:** {vector_config.get('provider', 'unknown')}
                **Config File:** {self.config_path}
                """)
                
                if vector_config.get('provider') == 'chromadb':
                    st.success("✅ Using ChromaDB (Streamlit Cloud Compatible)")
                else:
                    st.warning("⚠️ Using alternative vector database")
                    
            except Exception as e:
                st.error(f"Config error: {e}")
            
            st.divider()
            
            # Database stats
            st.subheader("📊 Database Status")
            stats = self.get_database_stats()
            if stats:
                st.metric("Total Documents", stats.get('total_documents', 0))
                st.caption(f"Provider: {stats.get('provider', 'unknown')}")
                st.caption(f"Collection: {stats.get('collection_name', 'unknown')}")
            else:
                st.warning("No database connection")
            
            st.divider()
            
            # Environment info
            st.subheader("🌐 Environment")
            if os.getenv('STREAMLIT_CLOUD'):
                st.success("Running on Streamlit Cloud")
            else:
                st.info("Running locally")
            
            # API Key status
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                st.success("✅ GROQ API Key configured")
            else:
                st.error("❌ GROQ_API_KEY not set")
            
            # SQLite version check
            try:
                import sqlite3
                sqlite_version = sqlite3.sqlite_version
                st.info(f"SQLite Version: {sqlite_version}")
                if sqlite_version >= "3.35.0":
                    st.success("✅ SQLite version compatible")
                else:
                    st.warning("⚠️ SQLite version may cause issues")
            except Exception as e:
                st.error(f"SQLite check failed: {e}")
    
    def render_main_interface(self):
        """Render the main application interface."""
        st.header("💬 Chat with Your Documents")
        
        # Initialize RAG pipeline if not already done
        if st.session_state.rag_pipeline is None:
            with st.spinner("Initializing RAG Pipeline..."):
                st.session_state.rag_pipeline = self.initialize_rag_pipeline(self.config_path)
        
        if st.session_state.rag_pipeline is None:
            st.error("❌ Failed to initialize RAG Pipeline. Check your configuration and API keys.")
            return
        
        # Chat interface
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
                        response = st.session_state.rag_pipeline.query(prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Error generating response: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    def render_upload_section(self):
        """Render the document upload section."""
        st.header("📁 Document Upload")
        
        # Cloud info
        st.markdown("""
        <div class="info-box">
            <strong>Streamlit Cloud Note:</strong> Document uploads are temporary in cloud environments. 
            Files will be processed and stored in ChromaDB, but uploaded files are not persisted between sessions.
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['pdf', 'txt', 'docx', 'json'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, DOCX, or JSON files to add to your knowledge base"
        )
        
        if uploaded_files:
            if st.button("📤 Process Uploaded Files"):
                if st.session_state.rag_pipeline is None:
                    st.error("❌ RAG Pipeline not initialized")
                    return
                
                with st.spinner("Processing files..."):
                    for uploaded_file in uploaded_files:
                        try:
                            # Save uploaded file temporarily
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Process the file
                            st.session_state.rag_pipeline.ingest_document(temp_path)
                            
                            # Clean up temp file
                            os.remove(temp_path)
                            
                            st.success(f"✅ Processed: {uploaded_file.name}")
                            
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {e}")
    
    def render_debug_section(self):
        """Render debug information."""
        st.header("🔍 Debug Information")
        
        with st.expander("System Information"):
            st.write(f"Python Version: {sys.version}")
            st.write(f"Streamlit Version: {st.__version__}")
            
            try:
                import chromadb
                st.write(f"ChromaDB Version: {chromadb.__version__}")
            except Exception as e:
                st.error(f"ChromaDB import error: {e}")
            
            try:
                import sqlite3
                st.write(f"SQLite Version: {sqlite3.sqlite_version}")
                st.write(f"SQLite Module: {sqlite3.__file__}")
            except Exception as e:
                st.error(f"SQLite error: {e}")
        
        with st.expander("Environment Variables"):
            env_vars = {
                'GROQ_API_KEY': os.getenv('GROQ_API_KEY', 'Not set'),
                'STREAMLIT_CLOUD': os.getenv('STREAMLIT_CLOUD', 'Not set'),
                'PYTHONPATH': os.getenv('PYTHONPATH', 'Not set')
            }
            for key, value in env_vars.items():
                if 'API_KEY' in key and value != 'Not set':
                    st.write(f"{key}: {'*' * 10} (hidden)")
                else:
                    st.write(f"{key}: {value}")
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        self.render_sidebar()
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📁 Upload", "🔍 Debug"])
        
        with tab1:
            self.render_main_interface()
        
        with tab2:
            self.render_upload_section()
        
        with tab3:
            self.render_debug_section()


def main():
    """Main entry point for the Streamlit Cloud compatible app."""
    app = StreamlitCloudRAGApp()
    app.run()


if __name__ == "__main__":
    main()
