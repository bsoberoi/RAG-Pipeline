# RAG (Retrieval-Augmented Generation) Project

A comprehensive RAG system for document-based question answering using ChromaDB, LangChain, and GROQ.

## 🏗️ Project Structure

```
rag_project/
├── data/
│   ├── raw/           # Original documents
│   ├── processed/     # Preprocessed documents
│   └── vectors/       # Vector database storage
├── src/
│   ├── ingestion/     # Document ingestion pipeline
│   ├── retrieval/     # Document retrieval system
│   ├── generation/    # Text generation components
│   └── utils/         # Utility functions
├── config/            # Configuration files
├── models/            # Model storage
├── notebooks/         # Jupyter notebooks for experimentation
├── scripts/           # Automation scripts
├── tests/             # Unit tests
├── logs/              # Application logs
└── docs/              # Documentation
```

## 🚀 Features

- **Document Ingestion**: Support for PDF, DOCX, TXT files
- **Vector Storage**: ChromaDB for efficient similarity search
- **Embeddings**: HuggingFace sentence-transformers
- **LLM Integration**: GROQ API for text generation
- **Retrieval**: Semantic search with configurable parameters
- **Generation**: Context-aware response generation

## 📋 Prerequisites

- Python 3.8+
- GROQ API Key

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   export GROQ_API_KEY="your_groq_api_key"
   ```

## 📖 Usage

### Basic Usage
```python
from src.rag_pipeline import RAGPipeline

# Initialize RAG system
rag = RAGPipeline()

# Add documents
rag.ingest_document("path/to/document.pdf")

# Query the system
response = rag.query("What is the main topic of the document?")
print(response)
```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request 