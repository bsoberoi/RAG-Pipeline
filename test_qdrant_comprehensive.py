#!/usr/bin/env python3
"""
Comprehensive test script for Qdrant RAG Pipeline.
Tests all aspects of the RAG system with Qdrant as the vector database.
"""

import sys
import os
from pathlib import Path
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db import create_vector_db
from src.utils.config_loader import ConfigLoader
from src.rag_pipeline import RAGPipeline
from src.ingestion.document_loader import DocumentLoader


def test_qdrant_connection():
    """Test basic Qdrant connection and collection operations."""
    print("🔌 Testing Qdrant Connection")
    print("=" * 50)
    
    try:
        # Load Qdrant configuration
        config = ConfigLoader("config/config.qdrant.yaml")
        vector_db_config = config.get_vector_db_config()
        
        # Create Qdrant client
        vector_db = create_vector_db(vector_db_config)
        
        # Get collection info
        info = vector_db.get_collection_info()
        print(f"✅ Qdrant connected successfully!")
        print(f"   Collection: {info['name']}")
        print(f"   Document count: {info['count']}")
        print(f"   Vector size: {info['vector_size']}")
        print(f"   Distance metric: {info['distance_metric']}")
        
        return vector_db, vector_db_config
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return None, None


def test_document_operations(vector_db):
    """Test adding and querying documents in Qdrant."""
    print("\n📄 Testing Document Operations")
    print("=" * 50)
    
    try:
        # Sample documents for testing
        test_documents = [
            "Artificial intelligence is transforming the way we work and live.",
            "Machine learning algorithms can process vast amounts of data efficiently.",
            "Natural language processing enables computers to understand human language.",
            "Deep learning models require significant computational resources.",
            "Vector databases are essential for similarity search in AI applications."
        ]
        
        # Sample metadata
        test_metadatas = [
            {"filename": "ai_intro.txt", "file_type": "text", "chunk_id": 0},
            {"filename": "ml_algorithms.txt", "file_type": "text", "chunk_id": 1},
            {"filename": "nlp_basics.txt", "file_type": "text", "chunk_id": 2},
            {"filename": "deep_learning.txt", "file_type": "text", "chunk_id": 3},
            {"filename": "vector_dbs.txt", "file_type": "text", "chunk_id": 4}
        ]
        
        # Generate IDs
        test_ids = [f"test_doc_{i}" for i in range(len(test_documents))]
        
        # Create embeddings (simplified - in real usage, use proper embedding model)
        # For testing, we'll create random embeddings
        import numpy as np
        test_embeddings = [np.random.rand(384).tolist() for _ in test_documents]
        
        print(f"📝 Adding {len(test_documents)} test documents...")
        
        # Add documents to Qdrant
        vector_db.add_documents(
            embeddings=test_embeddings,
            documents=test_documents,
            metadatas=test_metadatas,
            ids=test_ids
        )
        
        print("✅ Documents added successfully!")
        
        # Test querying
        print("\n🔍 Testing document queries...")
        
        # Create a query embedding (random for testing)
        query_embedding = [np.random.rand(384).tolist()]
        
        # Query for similar documents
        results = vector_db.query(query_embedding, n_results=3)
        
        print(f"✅ Query successful! Found {len(results['documents'][0])} results")
        
        # Display results
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            print(f"   Result {i+1}: {doc[:50]}... (distance: {distance:.4f})")
            print(f"   Metadata: {metadata['filename']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document operations failed: {e}")
        return False


def test_rag_pipeline():
    """Test the complete RAG pipeline with Qdrant."""
    print("\n🤖 Testing RAG Pipeline")
    print("=" * 50)
    
    try:
        # Initialize RAG pipeline with Qdrant config
        rag_pipeline = RAGPipeline("config/config.qdrant.yaml")
        
        print("✅ RAG Pipeline initialized successfully!")
        
        # Test a simple query
        test_query = "What is artificial intelligence?"
        print(f"🔍 Testing query: '{test_query}'")
        
        # Get response (this will use the LLM and retrieval)
        response = rag_pipeline.query(test_query)
        
        print(f"✅ RAG Pipeline response received!")
        print(f"Response: {response['response'][:200]}...")
        print(f"Sources found: {response['num_sources']}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Pipeline test failed: {e}")
        print("💡 Make sure you have the required API keys (GROQ_API_KEY)")
        return False


def test_document_loading():
    """Test loading documents from the data directory."""
    print("\n📂 Testing Document Loading")
    print("=" * 50)
    
    try:
        # Check if we have sample data
        data_dir = Path("data/raw")
        if not data_dir.exists():
            print("⚠️  No data directory found. Creating sample data...")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create sample JSON data
            sample_data = {
                "documents": [
                    {
                        "title": "Introduction to AI",
                        "content": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.",
                        "metadata": {"source": "test", "type": "introduction"}
                    },
                    {
                        "title": "Machine Learning Basics",
                        "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
                        "metadata": {"source": "test", "type": "tutorial"}
                    }
                ]
            }
            
            with open(data_dir / "sample_data.json", "w") as f:
                json.dump(sample_data, f, indent=2)
            
            print("✅ Sample data created!")
        
        # Test document loader
        loader = DocumentLoader()
        
        # Load documents from directory
        documents = loader.load_directory(data_dir)
        
        print(f"✅ Loaded {len(documents)} documents from data directory")
        
        for i, doc in enumerate(documents[:2]):  # Show first 2
            print(f"   Document {i+1}: {doc['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Document loading test failed: {e}")
        return False


def test_performance():
    """Test Qdrant performance with multiple queries."""
    print("\n⚡ Testing Performance")
    print("=" * 50)
    
    try:
        # Load configuration
        config = ConfigLoader("config/config.qdrant.yaml")
        vector_db_config = config.get_vector_db_config()
        vector_db = create_vector_db(vector_db_config)
        
        # Performance test queries
        test_queries = [
            "artificial intelligence",
            "machine learning algorithms",
            "natural language processing",
            "deep learning models",
            "vector databases"
        ]
        
        print(f"🚀 Running {len(test_queries)} performance queries...")
        
        import numpy as np
        total_time = 0
        
        for i, query in enumerate(test_queries):
            start_time = time.time()
            
            # Create random query embedding
            query_embedding = [np.random.rand(384).tolist()]
            
            # Query Qdrant
            results = vector_db.query(query_embedding, n_results=5)
            
            end_time = time.time()
            query_time = end_time - start_time
            total_time += query_time
            
            print(f"   Query {i+1}: {query_time:.4f}s ({len(results['documents'][0])} results)")
        
        avg_time = total_time / len(test_queries)
        print(f"✅ Performance test completed!")
        print(f"   Average query time: {avg_time:.4f}s")
        print(f"   Total time: {total_time:.4f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_collection_management():
    """Test Qdrant collection management operations."""
    print("\n🗂️  Testing Collection Management")
    print("=" * 50)
    
    try:
        # Load configuration
        config = ConfigLoader("config/config.qdrant.yaml")
        vector_db_config = config.get_vector_db_config()
        
        # Create a test collection
        test_config = vector_db_config.copy()
        test_config['collection_name'] = 'test_management'
        
        vector_db = create_vector_db(test_config)
        
        # Get collection info
        info = vector_db.get_collection_info()
        print(f"✅ Test collection created: {info['name']}")
        
        # Add some test data
        import numpy as np
        test_embeddings = [np.random.rand(384).tolist() for _ in range(3)]
        test_documents = ["Test doc 1", "Test doc 2", "Test doc 3"]
        test_metadatas = [{"test": True} for _ in range(3)]
        test_ids = ["test1", "test2", "test3"]
        
        vector_db.add_documents(test_embeddings, test_documents, test_metadatas, test_ids)
        
        # Verify data was added
        info_after = vector_db.get_collection_info()
        print(f"✅ Documents added. Collection count: {info_after['count']}")
        
        # Test query
        query_embedding = [np.random.rand(384).tolist()]
        results = vector_db.query(query_embedding, n_results=2)
        print(f"✅ Query successful: {len(results['documents'][0])} results")
        
        # Clean up - delete test collection
        vector_db.delete_collection()
        print("✅ Test collection deleted successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection management test failed: {e}")
        return False


def main():
    """Run all Qdrant tests."""
    print("🚀 Comprehensive Qdrant RAG Pipeline Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Basic connection
    vector_db, config = test_qdrant_connection()
    results.append(vector_db is not None)
    
    if vector_db:
        # Test 2: Document operations
        results.append(test_document_operations(vector_db))
        
        # Test 3: Collection management
        results.append(test_collection_management())
    
    # Test 4: Document loading
    results.append(test_document_loading())
    
    # Test 5: RAG Pipeline (may fail if no API keys)
    results.append(test_rag_pipeline())
    
    # Test 6: Performance
    if vector_db:
        results.append(test_performance())
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Qdrant tests passed!")
        print("\n✅ Your Qdrant RAG Pipeline is ready for use!")
        print("\nNext steps:")
        print("1. Set up your GROQ_API_KEY for LLM functionality")
        print("2. Add your documents to data/raw/")
        print("3. Run the Streamlit app: streamlit run app.streamlit.qdrant.py")
    else:
        print("⚠️  Some tests failed - check the output above")
        print("\nCommon issues:")
        print("- Make sure Qdrant is running: docker-compose -f docker-compose.qdrant.yml up -d")
        print("- Check your GROQ_API_KEY for LLM functionality")
        print("- Verify your configuration files")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
