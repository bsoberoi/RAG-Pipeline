#!/usr/bin/env python3
"""
Setup script for Qdrant Cloud integration.
This script helps you configure your RAG pipeline to use Qdrant Cloud.
"""

import os
import sys
from pathlib import Path
import yaml

def update_config_file(config_path, cluster_url, api_key=None):
    """Update a configuration file with Qdrant Cloud settings."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update Qdrant settings
        if 'vector_db' in config:
            config['vector_db']['url'] = cluster_url
            config['vector_db']['qdrant_url'] = cluster_url
            if api_key:
                config['vector_db']['qdrant_api_key'] = api_key
                config['vector_db']['api_key'] = api_key
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✅ Updated {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {config_path}: {e}")
        return False

def create_env_file(api_key):
    """Create a .env file with the Qdrant API key."""
    env_content = f"""# Qdrant Cloud Configuration
QDRANT_API_KEY={api_key}

# GROQ Configuration (if not already set)
# GROQ_API_KEY=your_groq_api_key_here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with Qdrant API key")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_qdrant_connection(cluster_url, api_key=None):
    """Test connection to Qdrant Cloud."""
    try:
        import qdrant_client
        
        if api_key:
            client = qdrant_client.QdrantClient(
                url=cluster_url,
                api_key=api_key
            )
        else:
            client = qdrant_client.QdrantClient(url=cluster_url)
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Successfully connected to Qdrant Cloud!")
        print(f"📊 Found {len(collections.collections)} collections")
        
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant Cloud: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Qdrant Cloud Setup")
    print("=" * 50)
    
    # Get user input
    print("\n📋 Please provide your Qdrant Cloud credentials:")
    cluster_url = input("Enter your Qdrant Cloud URL (e.g., https://your-cluster-id.qdrant.tech): ").strip()
    
    if not cluster_url:
        print("❌ Cluster URL is required!")
        return False
    
    api_key = input("Enter your Qdrant API key (press Enter to skip): ").strip()
    
    print(f"\n🔧 Updating configuration files...")
    
    # Update configuration files
    config_files = [
        "config/config.yaml",
        "config/config.streamlit.qdrant.yaml"
    ]
    
    success = True
    for config_file in config_files:
        if Path(config_file).exists():
            if not update_config_file(config_file, cluster_url, api_key):
                success = False
        else:
            print(f"⚠️  Configuration file not found: {config_file}")
    
    # Create .env file if API key provided
    if api_key:
        create_env_file(api_key)
    
    # Test connection
    print(f"\n🔍 Testing connection to Qdrant Cloud...")
    if test_qdrant_connection(cluster_url, api_key):
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set your GROQ_API_KEY environment variable")
        print("2. Run: python test_qdrant_comprehensive.py")
        print("3. Start your Streamlit app: python -m streamlit run app.streamlit.qdrant.py")
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")
        success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
