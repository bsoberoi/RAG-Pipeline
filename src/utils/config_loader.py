"""Configuration loader utility for the RAG system."""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """Utility class to load and manage configuration settings."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the config loader with the path to config file."""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key (e.g., 'llm.model')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get('llm', {})
    
    def get_embeddings_config(self) -> Dict[str, Any]:
        """Get embeddings configuration."""
        return self.config.get('embeddings', {})
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration."""
        return self.config.get('vector_db', {})
    
    def get_text_splitter_config(self) -> Dict[str, Any]:
        """Get text splitter configuration."""
        return self.config.get('text_splitter', {})
    
    def get_retrieval_config(self) -> Dict[str, Any]:
        """Get retrieval configuration."""
        return self.config.get('retrieval', {}) 