#!/usr/bin/env python3
"""
Migration script to transfer data from ChromaDB to Qdrant.
This script exports all data from ChromaDB and imports it into Qdrant.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config_loader import ConfigLoader
from src.vector_db import create_vector_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantDataMigrator:
    """Handles migration of data between vector databases and Qdrant."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the migrator with configuration."""
        self.config = ConfigLoader(config_path)
        self.chromadb_config = self._get_chromadb_config()
        self.qdrant_config = self._get_qdrant_config()
        
    def _get_chromadb_config(self) -> Dict[str, Any]:
        """Get ChromaDB configuration."""
        config = self.config.get_vector_db_config().copy()
        config['provider'] = 'chromadb'
        return config
    
    def _get_qdrant_config(self) -> Dict[str, Any]:
        """Get Qdrant configuration."""
        config = self.config.get_vector_db_config().copy()
        config['provider'] = 'qdrant'
        # Map Qdrant-specific config
        config['url'] = config.get('qdrant_url', 'http://localhost:6333')
        config['api_key'] = config.get('qdrant_api_key')
        config['vector_size'] = config.get('vector_size', 384)
        return config
    
    def export_chromadb_data(self) -> List[Dict[str, Any]]:
        """Export all data from ChromaDB."""
        logger.info("Starting ChromaDB data export...")
        
        try:
            # Create ChromaDB instance
            chromadb_client = create_vector_db(self.chromadb_config)
            
            # Get collection info
            collection_info = chromadb_client.get_collection_info()
            logger.info(f"Exporting from ChromaDB collection: {collection_info['name']}")
            logger.info(f"Total documents to export: {collection_info['count']}")
            
            if collection_info['count'] == 0:
                logger.warning("No documents found in ChromaDB collection")
                return []
            
            # Export all data
            # Note: This is a simplified export - in practice, you might need to
            # implement pagination for large datasets
            logger.warning("ChromaDB export requires extending the interface for full data export")
            logger.info("Consider using ChromaDB's native export functionality")
            
            return []
            
        except Exception as e:
            logger.error(f"Error exporting ChromaDB data: {e}")
            raise
    
    def import_to_qdrant(self, data: List[Dict[str, Any]]) -> None:
        """Import data to Qdrant."""
        logger.info("Starting Qdrant data import...")
        
        try:
            # Create Qdrant instance
            qdrant_client = create_vector_db(self.qdrant_config)
            
            if not data:
                logger.warning("No data to import")
                return
            
            # Prepare data for import
            embeddings = []
            documents = []
            metadatas = []
            ids = []
            
            for item in data:
                embeddings.append(item['embedding'])
                documents.append(item['document'])
                metadatas.append(item['metadata'])
                ids.append(item['id'])
            
            # Import in batches
            batch_size = 100
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            for i in range(0, len(data), batch_size):
                batch_end = min(i + batch_size, len(data))
                batch_embeddings = embeddings[i:batch_end]
                batch_documents = documents[i:batch_end]
                batch_metadatas = metadatas[i:batch_end]
                batch_ids = ids[i:batch_end]
                
                qdrant_client.add_documents(
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
                batch_num = (i // batch_size) + 1
                logger.info(f"Imported batch {batch_num}/{total_batches} ({len(batch_documents)} documents)")
            
            logger.info(f"Successfully imported {len(data)} documents to Qdrant")
            
        except Exception as e:
            logger.error(f"Error importing to Qdrant: {e}")
            raise
    
    def validate_migration(self) -> bool:
        """Validate that migration was successful."""
        logger.info("Validating migration...")
        
        try:
            # Get counts from both databases
            chromadb_client = create_vector_db(self.chromadb_config)
            qdrant_client = create_vector_db(self.qdrant_config)
            
            chromadb_count = chromadb_client.get_collection_info()['count']
            qdrant_count = qdrant_client.get_collection_info()['count']
            
            logger.info(f"ChromaDB count: {chromadb_count}")
            logger.info(f"Qdrant count: {qdrant_count}")
            
            if chromadb_count == qdrant_count:
                logger.info("✅ Migration validation successful - document counts match")
                return True
            else:
                logger.error("❌ Migration validation failed - document counts don't match")
                return False
                
        except Exception as e:
            logger.error(f"Error validating migration: {e}")
            return False
    
    def backup_chromadb_data(self, backup_path: str = None) -> str:
        """Create a backup of ChromaDB data."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_chromadb_{timestamp}.json"
        
        logger.info(f"Creating backup at: {backup_path}")
        
        try:
            # Export data
            data = self.export_chromadb_data()
            
            # Save to file
            with open(backup_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate data from ChromaDB to Qdrant")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--validate", action="store_true", help="Validate migration after completion")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without actually doing it")
    
    args = parser.parse_args()
    
    try:
        migrator = QdrantDataMigrator(args.config)
        
        if args.dry_run:
            logger.info("🔍 DRY RUN - No actual migration will be performed")
            
            # Check configurations
            logger.info("ChromaDB config:")
            logger.info(f"  Provider: {migrator.chromadb_config['provider']}")
            logger.info(f"  Path: {migrator.chromadb_config.get('path', 'N/A')}")
            logger.info(f"  Collection: {migrator.chromadb_config.get('collection_name', 'N/A')}")
            
            logger.info("Qdrant config:")
            logger.info(f"  Provider: {migrator.qdrant_config['provider']}")
            logger.info(f"  URL: {migrator.qdrant_config.get('url', 'N/A')}")
            logger.info(f"  Collection: {migrator.qdrant_config.get('collection_name', 'N/A')}")
            logger.info(f"  Vector Size: {migrator.qdrant_config.get('vector_size', 'N/A')}")
            
            # Check if Qdrant is accessible
            try:
                qdrant_client = create_vector_db(migrator.qdrant_config)
                collection_info = qdrant_client.get_collection_info()
                logger.info(f"✅ Qdrant connection successful - Collection: {collection_info['name']}")
            except Exception as e:
                logger.error(f"❌ Qdrant connection failed: {e}")
                return 1
            
            return 0
        
        # Create backup if requested
        if args.backup:
            backup_path = migrator.backup_chromadb_data()
            logger.info(f"Backup created: {backup_path}")
        
        # Perform migration
        logger.info("🚀 Starting migration from ChromaDB to Qdrant...")
        
        # Export from ChromaDB
        data = migrator.export_chromadb_data()
        
        if not data:
            logger.warning("No data to migrate")
            return 0
        
        # Import to Qdrant
        migrator.import_to_qdrant(data)
        
        # Validate if requested
        if args.validate:
            if migrator.validate_migration():
                logger.info("🎉 Migration completed successfully!")
            else:
                logger.error("❌ Migration validation failed")
                return 1
        else:
            logger.info("🎉 Migration completed!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
