# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy the RAG Pipeline to Streamlit Cloud with proper configuration for cloud environments.

## 🎯 Quick Fix for ChromaDB Error

The error you're encountering is due to ChromaDB's native dependencies not being compatible with Streamlit Cloud. Here's how to fix it:

## 📋 Step-by-Step Deployment

### 1. **Update Your Repository**

Make sure your repository includes these new files:
- `app.cloud.py` - Cloud-optimized Streamlit app
- `config/config.cloud.yaml` - Cloud configuration
- `requirements.cloud.txt` - Cloud-optimized dependencies
- `.streamlit/config.toml` - Streamlit configuration

### 2. **Set Up Weaviate Cloud (Recommended)**

Since ChromaDB doesn't work on Streamlit Cloud, you'll need to use Weaviate:

#### Option A: Weaviate Cloud Services (Recommended)
1. Go to [Weaviate Cloud Services](https://console.weaviate.cloud/)
2. Create a new cluster
3. Get your cluster URL and API key
4. Update `config/config.cloud.yaml`:
   ```yaml
   vector_db:
     provider: "weaviate"
     url: "https://your-cluster-url.weaviate.network"
     api_key: "your-weaviate-api-key"
     class_name: "Document"
   ```

#### Option B: Use a Free Weaviate Instance
You can use a free Weaviate instance from [Weaviate Cloud](https://console.weaviate.cloud/) or set up a free tier.

### 3. **Configure Environment Variables**

In your Streamlit Cloud app settings, add these secrets:

```
GROQ_API_KEY = your_groq_api_key_here
WEAVIATE_API_KEY = your_weaviate_api_key_here
```

### 4. **Update Streamlit Cloud Configuration**

In your Streamlit Cloud app settings:
- **Main file path**: `app.cloud.py`
- **Requirements file**: `requirements.cloud.txt`

### 5. **Deploy**

1. Push your changes to GitHub
2. Deploy on Streamlit Cloud
3. The app should now work without ChromaDB errors

## 🔧 Alternative: Local ChromaDB with Cloud App

If you want to keep using ChromaDB locally but deploy the web interface to the cloud:

### 1. **Create a Hybrid Configuration**

Create `config/config.hybrid.yaml`:
```yaml
# Hybrid configuration for local ChromaDB + cloud interface
vector_db:
  provider: "weaviate"  # Use Weaviate for cloud interface
  url: "https://your-weaviate-url"
  api_key: "your-api-key"
  class_name: "Document"
```

### 2. **Sync Data Between Systems**

Use the migration script to sync data:
```bash
# Export from local ChromaDB
python scripts/migrate_to_weaviate.py --backup

# Import to Weaviate Cloud
python scripts/migrate_to_weaviate.py --validate
```

## 🐛 Troubleshooting

### Common Issues:

1. **ChromaDB Import Error**
   - Solution: Use `app.cloud.py` and `requirements.cloud.txt`
   - Ensure you're using Weaviate instead of ChromaDB

2. **API Key Issues**
   - Check that `GROQ_API_KEY` is set in Streamlit Cloud secrets
   - Check that `WEAVIATE_API_KEY` is set if using Weaviate Cloud

3. **Configuration Issues**
   - Use `config/config.cloud.yaml` for cloud deployment
   - Verify your Weaviate URL and API key

4. **Memory Issues**
   - Streamlit Cloud has memory limits
   - Consider using smaller embedding models
   - Process documents in smaller batches

### Debug Steps:

1. **Check Logs**
   ```python
   # Add this to your app for debugging
   st.write("Environment variables:")
   st.write(f"GROQ_API_KEY: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
   st.write(f"WEAVIATE_API_KEY: {'Set' if os.getenv('WEAVIATE_API_KEY') else 'Not set'}")
   ```

2. **Test Configuration**
   ```python
   # Test your config
   try:
       config = ConfigLoader("config/config.cloud.yaml")
       st.success("Config loaded successfully")
   except Exception as e:
       st.error(f"Config error: {e}")
   ```

## 📊 Performance Optimization

### For Streamlit Cloud:

1. **Use Smaller Models**
   ```yaml
   embeddings:
     model: "sentence-transformers/all-MiniLM-L6-v2"  # Smaller model
   ```

2. **Optimize Chunk Sizes**
   ```yaml
   text_splitter:
     chunk_size: 500  # Smaller chunks
     chunk_overlap: 100
   ```

3. **Limit Results**
   ```yaml
   retrieval:
     max_results: 3  # Fewer results
   ```

## 🔄 Migration from Local to Cloud

If you have existing data in local ChromaDB:

1. **Export Data**
   ```bash
   python scripts/migrate_to_weaviate.py --backup
   ```

2. **Set Up Weaviate Cloud**
   - Create Weaviate Cloud account
   - Get API credentials

3. **Update Configuration**
   - Use `config/config.cloud.yaml`
   - Set Weaviate credentials

4. **Import Data**
   ```bash
   python scripts/migrate_to_weaviate.py --validate
   ```

5. **Deploy to Streamlit Cloud**
   - Use `app.cloud.py` as main file
   - Use `requirements.cloud.txt` for dependencies

## ✅ Success Checklist

- [ ] Using `app.cloud.py` as main file
- [ ] Using `requirements.cloud.txt` for dependencies
- [ ] Weaviate Cloud account set up
- [ ] Environment variables configured in Streamlit Cloud
- [ ] Configuration file updated with Weaviate credentials
- [ ] Data migrated from ChromaDB (if applicable)

## 🆘 Getting Help

If you're still having issues:

1. Check the Streamlit Cloud logs
2. Verify all environment variables are set
3. Test your Weaviate connection locally first
4. Ensure your configuration file is correct

The cloud-optimized version should resolve the ChromaDB compatibility issues you're experiencing!
