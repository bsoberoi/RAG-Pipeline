#!/usr/bin/env python3
"""
Test script to verify vector database implementations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db import create_vector_db, get_supported_providers
from src.utils.config_loader import ConfigLoader


def test_vector_db_factory():
    """Test the vector database factory."""
    print("🧪 Testing Vector Database Factory")
    print("=" * 50)
    
    # Test supported providers
    providers = get_supported_providers()
    print(f"Supported providers: {providers}")
    
    # Load configuration
    config = ConfigLoader("config/config.yaml")
    vector_db_config = config.get_vector_db_config()
    
    print(f"Current provider: {vector_db_config['provider']}")
    
    try:
        # Test creating vector database
        vector_db = create_vector_db(vector_db_config)
        print(f"✅ Successfully created {vector_db_config['provider']} instance")
        
        # Test getting collection info
        info = vector_db.get_collection_info()
        print(f"Collection info: {info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector database: {e}")
        return False


def test_chromadb():
    """Test ChromaDB implementation."""
    print("\n🧪 Testing ChromaDB Implementation")
    print("=" * 50)
    
    config = {
        'provider': 'chromadb',
        'path': './data/vectors',
        'collection_name': 'test_documents',
        'distance_metric': 'cosine'
    }
    
    try:
        vector_db = create_vector_db(config)
        info = vector_db.get_collection_info()
        print(f"✅ ChromaDB test successful: {info}")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False


def test_weaviate():
    """Test Weaviate implementation."""
    print("\n🧪 Testing Weaviate Implementation")
    print("=" * 50)
    
    config = {
        'provider': 'weaviate',
        'url': 'http://localhost:8080',
        'class_name': 'TestDocument'
    }
    
    try:
        vector_db = create_vector_db(config)
        info = vector_db.get_collection_info()
        print(f"✅ Weaviate test successful: {info}")
        return True
        
    except Exception as e:
        print(f"❌ Weaviate test failed: {e}")
        print("💡 Make sure Weaviate is running on localhost:8080")
        return False


def test_qdrant():
    """Test Qdrant implementation."""
    print("\n🧪 Testing Qdrant Implementation")
    print("=" * 50)
    
    config = {
        'provider': 'qdrant',
        'url': 'http://localhost:6333',
        'collection_name': 'TestDocument',
        'vector_size': 384
    }
    
    try:
        vector_db = create_vector_db(config)
        info = vector_db.get_collection_info()
        print(f"✅ Qdrant test successful: {info}")
        return True
        
    except Exception as e:
        print(f"❌ Qdrant test failed: {e}")
        print("💡 Make sure Qdrant is running on localhost:6333")
        return False


def main():
    """Run all tests."""
    print("🚀 Vector Database Implementation Tests")
    print("=" * 60)
    
    results = []
    
    # Test factory
    results.append(test_vector_db_factory())
    
    # Test ChromaDB
    results.append(test_chromadb())
    
    # Test Weaviate (may fail if not running)
    results.append(test_weaviate())
    
    # Test Qdrant (may fail if not running)
    results.append(test_qdrant())
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check the output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
