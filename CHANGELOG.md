# Changelog

All notable changes to the RAG Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-13

### Added
- **Qdrant Cloud Integration**: Full support for Qdrant Cloud as vector database backend
- **Multi-Vector Database Support**: Added Qdrant and Weaviate vector database options alongside ChromaDB
- **Cloud Deployment Ready**: Streamlit Cloud deployment configuration with Qdrant Cloud
- **Enhanced Document Processing**: Improved JSON file processing with proper list handling
- **Comprehensive Testing Suite**: Added extensive test scripts for all vector database backends
- **Migration Tools**: Scripts for migrating between different vector database backends
- **Cloud Setup Automation**: Interactive setup scripts for Qdrant Cloud configuration

### Fixed
- **JSON Processing Bug**: Fixed "list indices must be integers or slices, not str" error when processing JSON files
- **Document Ingestion**: Improved handling of JSON files containing arrays of documents
- **Vector Database Initialization**: Enhanced error handling and connection management
- **Streamlit Integration**: Fixed database initialization issues in Streamlit web interface

### Changed
- **Architecture**: Modularized vector database support with factory pattern
- **Configuration Management**: Enhanced configuration system with multiple backend support
- **Document Loader**: Improved JSON document processing to handle both single documents and arrays
- **RAG Pipeline**: Enhanced document ingestion to properly handle different data structures

### Technical Improvements
- **Vector Database Factory**: Implemented factory pattern for multiple vector database backends
- **Configuration Flexibility**: Support for multiple configuration files for different deployments
- **Error Handling**: Enhanced error handling and logging throughout the system
- **Testing Coverage**: Comprehensive test suite covering all major functionality
- **Documentation**: Added detailed setup guides for cloud deployments

### New Dependencies
- **Qdrant**: `qdrant-client` for Qdrant Cloud integration
- **Weaviate**: `weaviate-client` for Weaviate vector database support
- **Enhanced Testing**: Additional testing utilities and scripts

### Configuration Files
- `config/config.qdrant.yaml` - Qdrant Cloud configuration
- `config/config.streamlit.qdrant.yaml` - Streamlit with Qdrant Cloud
- `config/config.weaviate.yaml` - Weaviate configuration
- `config/config.cloud.yaml` - Cloud deployment configuration

### Migration and Setup Scripts
- `setup_qdrant_cloud.py` - Interactive Qdrant Cloud setup
- `migrate_to_qdrant_cloud.py` - Migration from local to Qdrant Cloud
- `migrate_to_weaviate.py` - Migration to Weaviate
- `switch_to_cloud.py` - Cloud deployment configuration

### Documentation
- `QDRANT_CLOUD_SETUP.md` - Comprehensive Qdrant Cloud setup guide
- `STREAMLIT_CLOUD_DEPLOYMENT.md` - Streamlit Cloud deployment guide
- `QDRANT_INTEGRATION.md` - Qdrant integration documentation

---

## [1.0.0] - 2025-09-08

### Added
- Initial release of RAG Pipeline v1.0.0
- Complete Streamlit web interface for document ingestion and querying
- Support for multiple document formats (PDF, DOCX, TXT, JSON)
- ChromaDB vector database integration
- GROQ API integration for LLM responses
- Interactive chat interface
- Document statistics and management
- Log management system
- System information and health checks
- Comprehensive error handling and user feedback
- Session state management
- File upload and directory ingestion capabilities
- Database clearing and maintenance tools

### Features
- **Dashboard**: Overview of system status and quick actions
- **Initialize**: System initialization with configuration options
- **Ingest Documents**: Multiple ingestion methods (upload, directory, auto-ingest)
- **Chat Interface**: Interactive conversation with documents
- **Single Query**: One-time question answering
- **Statistics**: Database metrics and storage information
- **Clear Database**: Safe database clearing with confirmation
- **Log Management**: Log file viewing, cleanup, and download
- **System Info**: Configuration and environment details
- **Stop App**: Graceful application shutdown

### Technical Details
- Built with Streamlit 1.49.0
- Uses LangChain for document processing and LLM integration
- ChromaDB for vector storage and similarity search
- GROQ API for fast LLM inference
- Comprehensive logging with Loguru
- Modular architecture with separate components for ingestion, processing, and querying
- Configuration management with YAML files
- Cross-platform compatibility (Windows, Linux, macOS)

### Dependencies
- Core: langchain, langchain-groq, langchain-text-splitters, langchain-huggingface
- Vector DB: chromadb
- ML/NLP: transformers, sentence-transformers, torch
- Document Processing: pypdf2, python-docx, pyyaml
- Web Interface: streamlit, fastapi, uvicorn
- Utilities: python-dotenv, tqdm, loguru, pandas, numpy

### Configuration
- Configuration file: `config/config.yaml`
- Log directory: `./logs`
- Vector database: `./data/vectors`
- Raw documents: `./data/raw`
- Environment variable: `GROQ_API_KEY` required

### Installation
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

### Usage
1. Set GROQ_API_KEY environment variable
2. Run `python -m streamlit run app.py`
3. Navigate to http://localhost:8501
4. Initialize the system
5. Ingest documents
6. Start querying and chatting

---

## Version History

- **v1.0.0** (2025-09-08): Initial release with full RAG pipeline functionality
