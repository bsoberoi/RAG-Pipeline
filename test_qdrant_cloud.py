#!/usr/bin/env python3
"""
Test script specifically for Qdrant Cloud connection.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db import create_vector_db
from src.utils.config_loader import ConfigLoader

def test_qdrant_cloud():
    """Test Qdrant Cloud connection."""
    print("☁️ Testing Qdrant Cloud Connection")
    print("=" * 50)
    
    try:
        # Load Qdrant Cloud configuration
        config = ConfigLoader("config/config.yaml")
        vector_db_config = config.get_vector_db_config()
        
        print(f"🔗 Qdrant URL: {vector_db_config['url']}")
        print(f"🔑 API Key: {'SET' if vector_db_config.get('api_key') else 'NOT SET'}")
        print(f"📦 Collection: {vector_db_config['collection_name']}")
        
        # Create Qdrant client
        vector_db = create_vector_db(vector_db_config)
        
        # Get collection info
        info = vector_db.get_collection_info()
        print(f"✅ Qdrant Cloud connected successfully!")
        print(f"   Collection: {info['name']}")
        print(f"   Document count: {info['count']}")
        print(f"   Vector size: {info['vector_size']}")
        print(f"   Distance metric: {info['distance_metric']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant Cloud connection failed: {e}")
        return False

def test_streamlit_config():
    """Test Streamlit configuration."""
    print("\n📋 Testing Streamlit Configuration")
    print("=" * 50)
    
    try:
        config = ConfigLoader("config/config.streamlit.qdrant.yaml")
        vector_db_config = config.get_vector_db_config()
        
        print(f"🔗 Streamlit Qdrant URL: {vector_db_config['url']}")
        print(f"🔑 Streamlit API Key: {'SET' if vector_db_config.get('api_key') else 'NOT SET'}")
        
        # Test connection
        vector_db = create_vector_db(vector_db_config)
        info = vector_db.get_collection_info()
        
        print(f"✅ Streamlit config working!")
        print(f"   Collection: {info['name']}")
        print(f"   Document count: {info['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit config test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Qdrant Cloud Connection Test")
    print("=" * 60)
    
    success1 = test_qdrant_cloud()
    success2 = test_streamlit_config()
    
    if success1 and success2:
        print("\n🎉 All Qdrant Cloud tests passed!")
        print("✅ Your Streamlit app should work with Qdrant Cloud")
    else:
        print("\n❌ Some tests failed - check the errors above")
    
    sys.exit(0 if (success1 and success2) else 1)
