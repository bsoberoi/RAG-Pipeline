#!/usr/bin/env python3
"""
Streamlit Cloud Optimized RAG Pipeline Application.
This version is optimized for cloud deployment with Weaviate.
"""

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
    page_title="RAG Pipeline - Cloud Edition",
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
</style>
""", unsafe_allow_html=True)

class CloudRAGStreamlitApp:
    """Cloud-optimized Streamlit web interface for the RAG Pipeline application."""
    
    def __init__(self):
        """Initialize the cloud-optimized RAG app."""
        self.config_path = self._get_config_path()
        self._setup_session_state()
    
    def _get_config_path(self) -> str:
        """Get the appropriate config path for cloud deployment."""
        # Try cloud config first, fallback to regular config
        cloud_config = "config/config.cloud.yaml"
        regular_config = "config/config.yaml"
        
        if os.path.exists(cloud_config):
            return cloud_config
        elif os.path.exists(regular_config):
            return regular_config
        else:
            st.error("❌ No configuration file found!")
            st.stop()
    
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
            <span class="cloud-badge">Cloud Edition</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Version info
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.caption(f"Version {version_info.get('version', '1.0.1')} | Cloud Optimized")
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Show current config
            st.subheader("Current Settings")
            try:
                config = ConfigLoader(self.config_path)
                vector_config = config.get_vector_db_config()
                
                st.info(f"""
                **Vector DB Provider:** {vector_config.get('provider', 'unknown')}
                **Config File:** {self.config_path}
                """)
                
                if vector_config.get('provider') == 'weaviate':
                    st.success("✅ Using Weaviate (Cloud Compatible)")
                else:
                    st.warning("⚠️ Using ChromaDB (May have cloud issues)")
                    
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
            
            weaviate_key = os.getenv('WEAVIATE_API_KEY')
            if weaviate_key:
                st.success("✅ Weaviate API Key configured")
            else:
                st.warning("⚠️ WEAVIATE_API_KEY not set")
    
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
            <strong>Cloud Deployment Note:</strong> Document uploads are temporary in cloud environments. 
            For persistent storage, consider using Weaviate Cloud with pre-uploaded documents.
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
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        self.render_sidebar()
        
        # Main tabs
        tab1, tab2 = st.tabs(["💬 Chat", "📁 Upload"])
        
        with tab1:
            self.render_main_interface()
        
        with tab2:
            self.render_upload_section()


def main():
    """Main entry point for the cloud-optimized Streamlit app."""
    app = CloudRAGStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
