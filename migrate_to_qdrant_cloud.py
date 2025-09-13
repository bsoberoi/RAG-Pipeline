#!/usr/bin/env python3
"""
Migration script to move data from local Qdrant to Qdrant Cloud.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.vector_db import create_vector_db
from src.utils.config_loader import ConfigLoader

def migrate_data():
    """Migrate data from local Qdrant to Qdrant Cloud."""
    print("🔄 Migrating data from local Qdrant to Qdrant Cloud")
    print("=" * 60)
    
    try:
        # Load local configuration
        print("📋 Loading local Qdrant configuration...")
        local_config = {
            'provider': 'qdrant',
            'url': 'http://localhost:6333',
            'collection_name': 'documents',
            'vector_size': 384,
            'distance_metric': 'cosine'
        }
        
        # Load cloud configuration
        print("📋 Loading Qdrant Cloud configuration...")
        cloud_config_loader = ConfigLoader("config/config.yaml")
        cloud_config = cloud_config_loader.get_vector_db_config()
        
        # Connect to local Qdrant
        print("🔗 Connecting to local Qdrant...")
        local_db = create_vector_db(local_config)
        local_info = local_db.get_collection_info()
        print(f"📊 Local collection: {local_info['name']} ({local_info['count']} documents)")
        
        # Connect to Qdrant Cloud
        print("☁️  Connecting to Qdrant Cloud...")
        cloud_db = create_vector_db(cloud_config)
        cloud_info = cloud_db.get_collection_info()
        print(f"📊 Cloud collection: {cloud_info['name']} ({cloud_info['count']} documents)")
        
        # Get all documents from local
        print("\n📥 Retrieving documents from local Qdrant...")
        
        # Create a dummy query to get all documents
        import numpy as np
        dummy_query = [np.random.rand(384).tolist()]
        
        # Get all documents (use a large number to get all)
        all_docs = local_db.query(dummy_query, n_results=1000)
        
        if not all_docs or not all_docs.get('documents') or not all_docs['documents'][0]:
            print("⚠️  No documents found in local Qdrant")
            return True
        
        documents = all_docs['documents'][0]
        metadatas = all_docs['metadatas'][0]
        ids = all_docs['ids'][0]
        
        print(f"📄 Found {len(documents)} documents to migrate")
        
        # Get embeddings for all documents
        print("🧮 Generating embeddings for documents...")
        from src.rag_pipeline import RAGPipeline
        
        # Initialize RAG pipeline for embeddings
        rag_pipeline = RAGPipeline("config/config.yaml")
        
        embeddings = []
        for doc in documents:
            embedding = rag_pipeline.embeddings.embed_query(doc)
            embeddings.append(embedding)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Upload to Qdrant Cloud
        print("☁️  Uploading documents to Qdrant Cloud...")
        
        # Upload in batches to avoid memory issues
        batch_size = 100
        total_uploaded = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            cloud_db.add_documents(
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            
            total_uploaded += len(batch_docs)
            print(f"📤 Uploaded {total_uploaded}/{len(documents)} documents...")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        final_cloud_info = cloud_db.get_collection_info()
        print(f"📊 Cloud collection now has: {final_cloud_info['count']} documents")
        
        if final_cloud_info['count'] >= len(documents):
            print("✅ Migration completed successfully!")
            
            # Test a query
            print("\n🧪 Testing query on Qdrant Cloud...")
            test_query = "artificial intelligence"
            test_embedding = [rag_pipeline.embeddings.embed_query(test_query)]
            results = cloud_db.query(test_embedding, n_results=3)
            
            if results and results.get('documents') and results['documents'][0]:
                print(f"✅ Query successful! Found {len(results['documents'][0])} results")
                print("🎉 Migration and verification completed!")
                return True
            else:
                print("⚠️  Query test failed, but documents were uploaded")
                return True
        else:
            print("❌ Migration verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function."""
    print("🚀 Qdrant Cloud Migration Tool")
    print("=" * 50)
    
    print("⚠️  This will migrate all data from your local Qdrant to Qdrant Cloud")
    print("📋 Make sure you have:")
    print("   1. Set up Qdrant Cloud account")
    print("   2. Updated config files with your cluster URL and API key")
    print("   3. Local Qdrant running with data")
    
    confirm = input("\n🤔 Do you want to continue? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Migration cancelled")
        return False
    
    success = migrate_data()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📋 Next steps:")
        print("1. Test your app with Qdrant Cloud")
        print("2. Update your Streamlit app configuration")
        print("3. Deploy to production")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
