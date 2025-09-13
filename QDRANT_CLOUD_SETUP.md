# ☁️ Qdrant Cloud Setup Guide

This guide will help you migrate from local Qdrant to Qdrant Cloud for better scalability and production deployment.

## 🚀 Step 1: Create Qdrant Cloud Account

### 1.1 Sign Up
1. Visit [Qdrant Cloud](https://cloud.qdrant.io/)
2. Click "Sign Up" and create your account
3. Verify your email address

### 1.2 Create a Cluster
1. Log in to your Qdrant Cloud dashboard
2. Click "Create Cluster"
3. Choose your plan (Free tier available)
4. Select your region
5. Click "Create Cluster"

### 1.3 Get Your Credentials
After creating your cluster, you'll get:
- **Cluster URL**: `https://your-cluster-id.qdrant.tech`
- **API Key**: `your-api-key-here`

## 🔧 Step 2: Configure Your Application

### 2.1 Run the Setup Script
```bash
python setup_qdrant_cloud.py
```

This script will:
- Ask for your cluster URL and API key
- Update all configuration files
- Create a `.env` file with your credentials
- Test the connection

### 2.2 Manual Configuration (Alternative)

If you prefer to configure manually:

#### Update `config/config.yaml`:
```yaml
vector_db:
  provider: "qdrant"
  url: "https://your-cluster-id.qdrant.tech"
  qdrant_url: "https://your-cluster-id.qdrant.tech"
  qdrant_api_key: "your-api-key-here"
  collection_name: "documents"
  distance_metric: "cosine"
  vector_size: 384
```

#### Update `config/config.streamlit.qdrant.yaml`:
```yaml
vector_db:
  provider: "qdrant"
  url: "https://your-cluster-id.qdrant.tech"
  api_key: "your-api-key-here"
  collection_name: "documents"
  distance_metric: "cosine"
  vector_size: 384
```

#### Create `.env` file:
```env
QDRANT_API_KEY=your-api-key-here
GROQ_API_KEY=your-groq-api-key-here
```

## 📦 Step 3: Migrate Your Data

### 3.1 Run the Migration Script
```bash
python migrate_to_qdrant_cloud.py
```

This script will:
- Connect to your local Qdrant
- Retrieve all documents and embeddings
- Upload everything to Qdrant Cloud
- Verify the migration was successful

### 3.2 Manual Migration (Alternative)

If you prefer to migrate manually:

1. **Export from local Qdrant**:
   ```python
   from src.vector_db import create_vector_db
   
   local_config = {
       'provider': 'qdrant',
       'url': 'http://localhost:6333',
       'collection_name': 'documents'
   }
   
   local_db = create_vector_db(local_config)
   # Get all documents...
   ```

2. **Import to Qdrant Cloud**:
   ```python
   cloud_config = {
       'provider': 'qdrant',
       'url': 'https://your-cluster-id.qdrant.tech',
       'api_key': 'your-api-key',
       'collection_name': 'documents'
   }
   
   cloud_db = create_vector_db(cloud_config)
   # Upload documents...
   ```

## 🧪 Step 4: Test Your Setup

### 4.1 Test Connection
```bash
python test_qdrant_comprehensive.py
```

### 4.2 Test Streamlit App
```bash
python -m streamlit run app.streamlit.qdrant.py
```

### 4.3 Verify Data
1. Open http://localhost:8501
2. Go to "📊 Statistics" page
3. Check that your documents are visible
4. Test a query in "💬 Chat Interface"

## 🚀 Step 5: Deploy to Production

### 5.1 Streamlit Cloud Deployment

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Qdrant Cloud support"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set environment variables:
     - `QDRANT_API_KEY`: Your Qdrant Cloud API key
     - `GROQ_API_KEY`: Your GROQ API key

3. **Update configuration**:
   - Use `config/config.streamlit.qdrant.yaml`
   - Ensure it points to your Qdrant Cloud cluster

### 5.2 Other Deployment Options

- **Docker**: Use the provided Dockerfile
- **AWS/GCP/Azure**: Deploy with your preferred cloud provider
- **VPS**: Deploy on any virtual private server

## 📊 Qdrant Cloud Benefits

### ✅ **Advantages over Local Qdrant**:
- **Scalability**: Handle millions of vectors
- **Reliability**: 99.9% uptime SLA
- **Performance**: Optimized for production workloads
- **Security**: Enterprise-grade security
- **Backup**: Automatic backups and disaster recovery
- **Monitoring**: Built-in monitoring and alerting
- **Global**: Deploy in multiple regions

### 📈 **Pricing**:
- **Free Tier**: 1GB storage, 1M vectors
- **Paid Plans**: Starting from $25/month
- **Enterprise**: Custom pricing for large deployments

## 🔧 Configuration Reference

### Environment Variables
```env
# Required
QDRANT_API_KEY=your-qdrant-api-key
GROQ_API_KEY=your-groq-api-key

# Optional
QDRANT_URL=https://your-cluster-id.qdrant.tech
```

### Configuration Files
- `config/config.yaml` - Main configuration
- `config/config.streamlit.qdrant.yaml` - Streamlit-specific
- `.env` - Environment variables

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Check your cluster URL
   - Verify your API key
   - Ensure your cluster is running

2. **Authentication Error**:
   - Verify your API key is correct
   - Check if your API key has expired
   - Ensure you have the right permissions

3. **Migration Failed**:
   - Check your local Qdrant is running
   - Verify you have data to migrate
   - Check your internet connection

4. **Performance Issues**:
   - Check your cluster size
   - Monitor your usage in Qdrant Cloud dashboard
   - Consider upgrading your plan

### Debug Commands

```bash
# Test Qdrant Cloud connection
python -c "import qdrant_client; client = qdrant_client.QdrantClient('https://your-cluster-id.qdrant.tech', api_key='your-key'); print(client.get_collections())"

# Check environment variables
python -c "import os; print('QDRANT_API_KEY:', 'SET' if os.getenv('QDRANT_API_KEY') else 'NOT SET')"

# Test configuration loading
python -c "from src.utils.config_loader import ConfigLoader; config = ConfigLoader('config/config.yaml'); print(config.get_vector_db_config())"
```

## 📚 Additional Resources

- [Qdrant Cloud Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [GROQ API Documentation](https://console.groq.com/docs)

## 🎉 Success Checklist

- [ ] Qdrant Cloud account created
- [ ] Cluster created and running
- [ ] Configuration files updated
- [ ] Environment variables set
- [ ] Data migrated successfully
- [ ] Connection tested
- [ ] Streamlit app working
- [ ] Production deployment ready

---

**🚀 Your RAG Pipeline is now ready for production with Qdrant Cloud!**
