# 🚀 Qdrant Vector Database Integration

This document describes the integration of Qdrant as a vector database option in the RAG Pipeline.

## 📋 Overview

Qdrant is now fully integrated as a third vector database option alongside ChromaDB and Weaviate. It provides high-performance vector search capabilities with excellent scalability.

## 🏗️ Implementation Details

### **Files Added/Modified:**

#### **New Files:**
- `src/vector_db/qdrant_client.py` - Qdrant implementation
- `config/config.qdrant.yaml` - Qdrant-specific configuration
- `docker-compose.qdrant.yml` - Docker setup for local Qdrant
- `scripts/migrate_to_qdrant.py` - Migration script from ChromaDB to Qdrant
- `QDRANT_INTEGRATION.md` - This documentation

#### **Modified Files:**
- `src/vector_db/__init__.py` - Added Qdrant to factory pattern
- `config/config.yaml` - Added Qdrant configuration options
- `requirements.txt` - Added qdrant-client dependency
- `pyproject.toml` - Added qdrant-client dependency
- `README.md` - Updated documentation
- `test_vector_db.py` - Added Qdrant tests

## ⚙️ Configuration

### **Basic Configuration:**
```yaml
vector_db:
  provider: "qdrant"
  url: "http://localhost:6333"
  collection_name: "documents"
  distance_metric: "cosine"
  vector_size: 384
```

### **Qdrant Cloud Configuration:**
```yaml
vector_db:
  provider: "qdrant"
  url: "https://your-cluster-url.qdrant.tech"
  api_key: "your-api-key"
  collection_name: "documents"
  distance_metric: "cosine"
  vector_size: 384
```

## 🚀 Quick Start

### **Option 1: Local Qdrant Instance**

1. **Start Qdrant with Docker:**
   ```bash
   docker-compose -f docker-compose.qdrant.yml up -d
   ```

2. **Update Configuration:**
   ```yaml
   vector_db:
     provider: "qdrant"
     url: "http://localhost:6333"
     collection_name: "documents"
     vector_size: 384
   ```

3. **Run the Application:**
   ```bash
   python app.py
   ```

### **Option 2: Qdrant Cloud**

1. **Sign up for Qdrant Cloud:**
   - Visit [Qdrant Cloud](https://cloud.qdrant.io/)
   - Create a new cluster
   - Get your API key and cluster URL

2. **Update Configuration:**
   ```yaml
   vector_db:
     provider: "qdrant"
     url: "https://your-cluster-url.qdrant.tech"
     api_key: "your-api-key"
     collection_name: "documents"
     vector_size: 384
   ```

3. **Set Environment Variable:**
   ```bash
   export QDRANT_API_KEY="your-api-key"
   ```

## 🔧 Key Features

### **Unified Interface**
Qdrant uses the same interface as ChromaDB and Weaviate:
```python
# Same methods for all providers
vector_db.add_documents(embeddings, documents, metadatas, ids)
results = vector_db.query(query_embeddings, n_results)
info = vector_db.get_collection_info()
```

### **Distance Metrics**
Supported distance metrics:
- `cosine` - Cosine similarity (default)
- `euclidean` - Euclidean distance
- `dot` - Dot product

### **Vector Dimensions**
- Default: 384 (for sentence-transformers/all-MiniLM-L6-v2)
- Configurable via `vector_size` parameter
- Automatically creates collections with correct dimensions

## 📊 Performance Benefits

### **Qdrant Advantages:**
- ✅ **High Performance** - Optimized for large-scale vector search
- ✅ **Scalability** - Handles millions of vectors efficiently
- ✅ **Cloud Ready** - Native cloud deployment options
- ✅ **Memory Efficient** - Optimized memory usage
- ✅ **REST API** - Easy integration and monitoring
- ✅ **Filtering** - Advanced filtering capabilities

### **Use Cases:**
- Large-scale document collections
- High-throughput applications
- Cloud deployments
- Production environments requiring high performance

## 🔄 Migration

### **From ChromaDB to Qdrant:**

1. **Backup and Migrate:**
   ```bash
   python scripts/migrate_to_qdrant.py --backup --validate
   ```

2. **Dry Run:**
   ```bash
   python scripts/migrate_to_qdrant.py --dry-run
   ```

3. **Update Configuration:**
   Change `provider` from `"chromadb"` to `"qdrant"`

## 🧪 Testing

### **Test Qdrant Implementation:**
```bash
python test_vector_db.py
```

### **Manual Testing:**
```python
from src.vector_db import create_vector_db

config = {
    'provider': 'qdrant',
    'url': 'http://localhost:6333',
    'collection_name': 'test',
    'vector_size': 384
}

vector_db = create_vector_db(config)
info = vector_db.get_collection_info()
print(f"Qdrant info: {info}")
```

## 🐳 Docker Deployment

### **Local Development:**
```bash
# Start Qdrant
docker-compose -f docker-compose.qdrant.yml up -d

# Check status
curl http://localhost:6333/health
```

### **Production Deployment:**
```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:v1.15.0
    ports:
      - "6333:6333"
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  qdrant_data:
```

## 🔍 Monitoring

### **Health Check:**
```bash
curl http://localhost:6333/health
```

### **Collection Info:**
```bash
curl http://localhost:6333/collections
```

### **Metrics:**
```bash
curl http://localhost:6333/metrics
```

## 🆚 Comparison

| Feature | ChromaDB | Weaviate | Qdrant |
|---------|----------|----------|--------|
| **Performance** | Good | Excellent | Excellent |
| **Scalability** | Limited | Good | Excellent |
| **Cloud Support** | Limited | Excellent | Excellent |
| **Memory Usage** | High | Medium | Low |
| **Setup Complexity** | Low | Medium | Low |
| **API** | Python | GraphQL | REST |
| **Filtering** | Basic | Advanced | Advanced |

## 🚨 Troubleshooting

### **Common Issues:**

1. **Connection Refused:**
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   curl http://localhost:6333/health
   ```

2. **Vector Size Mismatch:**
   ```yaml
   # Ensure vector_size matches your embedding model
   vector_size: 384  # for sentence-transformers/all-MiniLM-L6-v2
   ```

3. **Collection Not Found:**
   ```python
   # Collections are created automatically
   # Check collection exists
   curl http://localhost:6333/collections
   ```

### **Debug Commands:**
```bash
# Check Qdrant logs
docker logs qdrant_container_name

# Test connection
python -c "import qdrant_client; client = qdrant_client.QdrantClient('http://localhost:6333'); print(client.get_collections())"
```

## 📚 Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Docker Hub - Qdrant](https://hub.docker.com/r/qdrant/qdrant)

## ✅ Success Checklist

- [ ] Qdrant client installed (`qdrant-client==1.15.1`)
- [ ] Qdrant server running (local or cloud)
- [ ] Configuration updated with Qdrant settings
- [ ] Vector size matches embedding model
- [ ] Collection created successfully
- [ ] Documents can be added and queried
- [ ] Migration completed (if applicable)

The Qdrant integration provides a powerful, scalable alternative to ChromaDB and Weaviate, especially suitable for production environments requiring high performance and scalability.
