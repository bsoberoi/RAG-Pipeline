#!/usr/bin/env python3
"""
Test script to verify Streamlit app initialization with local Qdrant.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag_pipeline import RAGPipeline
from src.utils.config_loader import ConfigLoader


def test_streamlit_initialization():
    """Test that the Streamlit app can initialize properly with local Qdrant."""
    print("🧪 Testing Streamlit App Initialization")
    print("=" * 50)
    
    try:
        # Test with the Streamlit Qdrant config
        config_path = "config/config.streamlit.qdrant.yaml"
        print(f"📋 Using config: {config_path}")
        
        # Load configuration
        config = ConfigLoader(config_path)
        vector_db_config = config.get_vector_db_config()
        
        print(f"🔗 Qdrant URL: {vector_db_config.get('url')}")
        print(f"📦 Collection: {vector_db_config.get('collection_name')}")
        print(f"📏 Vector Size: {vector_db_config.get('vector_size')}")
        
        # Test RAG Pipeline initialization
        print("\n🚀 Initializing RAG Pipeline...")
        rag_pipeline = RAGPipeline(config_path)
        
        print("✅ RAG Pipeline initialized successfully!")
        
        # Test collection info
        stats = rag_pipeline.get_collection_stats()
        print(f"📊 Collection stats: {stats}")
        
        # Test a simple query
        print("\n🔍 Testing query...")
        test_query = "What is artificial intelligence?"
        response = rag_pipeline.query(test_query)
        
        print(f"✅ Query successful!")
        print(f"📝 Response: {response['response'][:100]}...")
        print(f"📚 Sources found: {response['num_sources']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = test_streamlit_initialization()
    if success:
        print("\n🎉 Streamlit app initialization test passed!")
        print("✅ You can now use the web interface at http://localhost:8501")
    else:
        print("\n❌ Streamlit app initialization test failed!")
        print("💡 Check the error message above for details")
    
    sys.exit(0 if success else 1)
