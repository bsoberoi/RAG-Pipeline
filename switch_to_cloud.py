#!/usr/bin/env python3
"""
Script to switch the RAG Pipeline to cloud-optimized configuration.
This helps resolve ChromaDB compatibility issues on Streamlit Cloud.
"""

import os
import shutil
from pathlib import Path


def switch_to_cloud_config():
    """Switch to cloud-optimized configuration."""
    print("🚀 Switching to Cloud-Optimized Configuration")
    print("=" * 50)
    
    # Check if cloud config exists
    cloud_config = Path("config/config.cloud.yaml")
    if not cloud_config.exists():
        print("❌ Cloud configuration file not found!")
        print("Please ensure config/config.cloud.yaml exists")
        return False
    
    # Backup current config
    current_config = Path("config/config.yaml")
    if current_config.exists():
        backup_path = Path("config/config.yaml.backup")
        shutil.copy2(current_config, backup_path)
        print(f"✅ Backed up current config to {backup_path}")
    
    # Copy cloud config to main config
    shutil.copy2(cloud_config, current_config)
    print("✅ Switched to cloud configuration")
    
    # Check if cloud requirements exist
    cloud_requirements = Path("requirements.cloud.txt")
    if cloud_requirements.exists():
        print("📋 Cloud requirements file found:")
        print("   - Use 'requirements.cloud.txt' for Streamlit Cloud deployment")
        print("   - This removes ChromaDB dependencies that cause cloud issues")
    
    # Check if cloud app exists
    cloud_app = Path("app.cloud.py")
    if cloud_app.exists():
        print("🌐 Cloud app found:")
        print("   - Use 'app.cloud.py' as main file for Streamlit Cloud")
        print("   - This is optimized for cloud deployment")
    
    print("\n📝 Next Steps:")
    print("1. Set up Weaviate Cloud account (https://console.weaviate.cloud/)")
    print("2. Update config/config.yaml with your Weaviate credentials")
    print("3. Set environment variables in Streamlit Cloud:")
    print("   - GROQ_API_KEY")
    print("   - WEAVIATE_API_KEY")
    print("4. Deploy using app.cloud.py and requirements.cloud.txt")
    
    return True


def switch_to_local_config():
    """Switch back to local configuration."""
    print("🏠 Switching to Local Configuration")
    print("=" * 50)
    
    # Check if backup exists
    backup_config = Path("config/config.yaml.backup")
    if not backup_config.exists():
        print("❌ No backup configuration found!")
        return False
    
    # Restore backup
    current_config = Path("config/config.yaml")
    shutil.copy2(backup_config, current_config)
    print("✅ Restored local configuration")
    
    print("\n📝 Local configuration restored")
    print("You can now use ChromaDB locally")
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Switch RAG Pipeline configuration")
    parser.add_argument("--to-cloud", action="store_true", help="Switch to cloud configuration")
    parser.add_argument("--to-local", action="store_true", help="Switch to local configuration")
    parser.add_argument("--status", action="store_true", help="Show current configuration status")
    
    args = parser.parse_args()
    
    if args.status:
        print("📊 Configuration Status")
        print("=" * 30)
        
        config_file = Path("config/config.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                if 'provider: "weaviate"' in content:
                    print("🌐 Current: Cloud configuration (Weaviate)")
                elif 'provider: "chromadb"' in content:
                    print("🏠 Current: Local configuration (ChromaDB)")
                else:
                    print("❓ Current: Unknown configuration")
        else:
            print("❌ No configuration file found")
        
        # Check for cloud files
        cloud_files = [
            "config/config.cloud.yaml",
            "requirements.cloud.txt", 
            "app.cloud.py"
        ]
        
        print("\n📁 Cloud files available:")
        for file in cloud_files:
            if Path(file).exists():
                print(f"✅ {file}")
            else:
                print(f"❌ {file}")
        
        return 0
    
    if args.to_cloud:
        success = switch_to_cloud_config()
        return 0 if success else 1
    
    elif args.to_local:
        success = switch_to_local_config()
        return 0 if success else 1
    
    else:
        print("RAG Pipeline Configuration Switcher")
        print("=" * 40)
        print("Usage:")
        print("  python switch_to_cloud.py --to-cloud    # Switch to cloud config")
        print("  python switch_to_cloud.py --to-local    # Switch to local config")
        print("  python switch_to_cloud.py --status      # Show current status")
        return 0


if __name__ == "__main__":
    exit(main())
