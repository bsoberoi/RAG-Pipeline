# Changelog

All notable changes to the RAG Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
