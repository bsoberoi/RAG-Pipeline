# 🚀 Streamlit Cloud Deployment with Qdrant

This guide explains how to deploy your RAG Pipeline to Streamlit Cloud using Qdrant as the vector database.

## 📋 Prerequisites

1. **Qdrant Cloud Account**: Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. **Streamlit Cloud Account**: Sign up at [Streamlit Cloud](https://share.streamlit.io/)
3. **GitHub Repository**: Your code should be in a GitHub repository

## 🔧 Setup Steps

### **Step 1: Create Qdrant Cloud Cluster**

1. **Sign up for Qdrant Cloud:**
   - Go to [Qdrant Cloud](https://cloud.qdrant.io/)
   - Create a new account or sign in
   - Create a new cluster

2. **Get your cluster details:**
   - **Cluster URL**: `https://your-cluster-id.qdrant.tech`
   - **API Key**: Copy your API key from the dashboard

### **Step 2: Prepare Your Repository**

1. **Use the Qdrant-optimized files:**
   - `app.streamlit.qdrant.py` - Streamlit app optimized for Qdrant
   - `config/config.streamlit.qdrant.yaml` - Configuration for Qdrant Cloud
   - `requirements.streamlit.qdrant.txt` - Dependencies without ChromaDB

2. **Update configuration:**
   ```yaml
   # In config/config.streamlit.qdrant.yaml
   vector_db:
     provider: "qdrant"
     url: "https://your-cluster-id.qdrant.tech"  # Your Qdrant Cloud URL
     api_key: null  # Will be set from environment variable
     collection_name: "documents"
     vector_size: 384
   ```

### **Step 3: Deploy to Streamlit Cloud**

1. **Connect your GitHub repository:**
   - Go to [Streamlit Cloud](https://share.streamlit.io/)
   - Click "New app"
   - Connect your GitHub repository

2. **Configure the deployment:**
   - **Main file path**: `app.streamlit.qdrant.py`
   - **Branch**: `main` (or your preferred branch)

3. **Set environment variables:**
   - `GROQ_API_KEY`: Your GROQ API key
   - `QDRANT_API_KEY`: Your Qdrant Cloud API key

### **Step 4: Environment Variables**

In your Streamlit Cloud app settings, add these environment variables:

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
QDRANT_API_KEY=your_qdrant_cloud_api_key_here
```

## 🎯 Configuration Options

### **Option 1: Qdrant Cloud (Recommended)**

**Pros:**
- ✅ Fully managed service
- ✅ High availability and scalability
- ✅ No server maintenance
- ✅ Built-in backup and monitoring

**Cons:**
- ❌ Requires paid subscription for production use
- ❌ Internet dependency

**Setup:**
```yaml
vector_db:
  provider: "qdrant"
  url: "https://your-cluster-id.qdrant.tech"
  api_key: "${QDRANT_API_KEY}"  # From environment variable
  collection_name: "documents"
  vector_size: 384
```

### **Option 2: Self-hosted Qdrant (Advanced)**

**Pros:**
- ✅ Full control over your data
- ✅ No external dependencies
- ✅ Cost-effective for large deployments

**Cons:**
- ❌ Requires server management
- ❌ Need to handle backups and monitoring
- ❌ More complex setup

**Setup:**
```yaml
vector_db:
  provider: "qdrant"
  url: "https://your-qdrant-server.com"
  api_key: "${QDRANT_API_KEY}"
  collection_name: "documents"
  vector_size: 384
```

## 🔄 Migration from Local to Cloud

### **Step 1: Export Local Data**

If you have existing data in your local ChromaDB:

```bash
# Create a migration script
python scripts/migrate_to_qdrant.py --backup --validate
```

### **Step 2: Import to Qdrant Cloud**

1. **Use the migration script** to transfer data
2. **Or manually re-upload** documents through the Streamlit interface

## 🚀 Deployment Commands

### **Local Testing with Qdrant Cloud**

```bash
# Set environment variables
export GROQ_API_KEY="your_groq_key"
export QDRANT_API_KEY="your_qdrant_key"

# Run the app
streamlit run app.streamlit.qdrant.py
```

### **Streamlit Cloud Deployment**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Qdrant Cloud deployment support"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [Streamlit Cloud](https://share.streamlit.io/)
   - Create new app
   - Select your repository
   - Set main file: `app.streamlit.qdrant.py`
   - Add environment variables

## 🔍 Troubleshooting

### **Common Issues:**

1. **"Qdrant connection failed"**
   - Check your Qdrant Cloud URL
   - Verify your API key is correct
   - Ensure your cluster is running

2. **"GROQ API key not found"**
   - Set the `GROQ_API_KEY` environment variable
   - Verify the key is valid

3. **"Collection not found"**
   - Collections are created automatically
   - Check your collection name in the config

### **Debug Commands:**

```bash
# Test Qdrant connection
python -c "
import os
from qdrant_client import QdrantClient
client = QdrantClient(
    url=os.getenv('QDRANT_URL', 'https://your-cluster.qdrant.tech'),
    api_key=os.getenv('QDRANT_API_KEY')
)
print('Collections:', client.get_collections())
"
```

## 📊 Monitoring

### **Qdrant Cloud Dashboard:**
- Monitor cluster health
- View usage statistics
- Check API usage and limits

### **Streamlit Cloud:**
- View app logs
- Monitor performance
- Check deployment status

## 💰 Cost Considerations

### **Qdrant Cloud Pricing:**
- **Free tier**: 1 cluster, 1GB storage
- **Paid plans**: Start from $25/month
- **Usage-based**: Pay for what you use

### **Streamlit Cloud:**
- **Free tier**: Public apps only
- **Pro plan**: Private apps, custom domains

## 🔐 Security Best Practices

1. **Environment Variables:**
   - Never commit API keys to your repository
   - Use Streamlit Cloud's environment variable system

2. **Qdrant Security:**
   - Use HTTPS URLs only
   - Rotate API keys regularly
   - Monitor API usage

3. **Data Privacy:**
   - Review Qdrant Cloud's data processing agreement
   - Consider data residency requirements

## 🎉 Success Checklist

- [ ] Qdrant Cloud cluster created
- [ ] API keys obtained and secured
- [ ] Configuration files updated
- [ ] Environment variables set
- [ ] App deployed to Streamlit Cloud
- [ ] Connection tested successfully
- [ ] Documents can be uploaded and queried

## 📚 Additional Resources

- [Qdrant Cloud Documentation](https://cloud.qdrant.io/docs/)
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)

Your RAG Pipeline is now ready for cloud deployment with Qdrant! 🚀

