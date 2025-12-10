# 🚀 HuggingFace Spaces Deployment Guide

## Overview
This guide helps you deploy the SAP Chatbot to **HuggingFace Spaces** for free multi-user access.

---

## **Step 1: Prepare Your Data on HuggingFace Hub**

### 1.1 Create a HuggingFace Account
- Go to https://huggingface.co
- Sign up (free)
- Create an API token: https://huggingface.co/settings/tokens

### 1.2 Create a Dataset Repository
```bash
# Install HuggingFace CLI
pip install huggingface-hub

# Login to HuggingFace
huggingface-cli login
# Paste your token when prompted
```

### 1.3 Upload Your Dataset
Create a new dataset repo on HuggingFace:
1. Go to https://huggingface.co/datasets?type=private
2. Click "New Dataset"
3. Choose a name: `sap-chatbot-data`
4. Set to **Private** (recommended)
5. Create

### 1.4 Upload Data Files
```bash
# From your local machine, upload the data files
cd /Users/akshay/sap-chatboot

huggingface-cli upload \
  your-username/sap-chatbot-data \
  data/rag_index.faiss \
  data/rag_index.faiss

huggingface-cli upload \
  your-username/sap-chatbot-data \
  data/rag_metadata.pkl \
  data/rag_metadata.pkl

huggingface-cli upload \
  your-username/sap-chatbot-data \
  data/sap_dataset.json \
  data/sap_dataset.json
```

Or drag & drop files in the HuggingFace web interface.

---

## **Step 2: Push Code to GitHub**

### 2.1 Create a GitHub Repository
```bash
cd /Users/akshay/sap-chatboot

git init
git add .
git commit -m "Initial SAP Chatbot commit"

# Create repo on GitHub
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/sap-chatbot.git
git branch -M main
git push -u origin main
```

### 2.2 Create `.env` in GitHub
⚠️ **IMPORTANT**: Never commit actual secrets to GitHub!

Create `.github/workflows/` or just add to your Space secrets directly (see Step 3).

---

## **Step 3: Create HuggingFace Space**

### 3.1 Create New Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in details:
   - **Space name**: `sap-chatbot` (or your choice)
   - **License**: Apache 2.0 (or your preference)
   - **Space SDK**: Streamlit
   - **Visibility**: Public or Private
4. Click "Create Space"

### 3.2 Connect GitHub Repository
1. In the Space settings, go to "Settings" → "Linked Repositories"
2. Connect your GitHub repo
3. Choose your GitHub repository
4. Space will auto-deploy on each push!

**OR** (Alternative) - Upload files directly:
1. Clone the space repo: `git clone https://huggingface.co/spaces/USERNAME/sap-chatbot`
2. Copy your files there
3. Push with git

### 3.3 Add Secrets
In Space settings, go to **"Secrets"** and add:

| Variable | Value |
|----------|-------|
| `HF_API_TOKEN` | Your HuggingFace API token (https://huggingface.co/settings/tokens) |
| `HF_DATASET_REPO` | `your-username/sap-chatbot-data` |
| `LLM_PROVIDER` | `huggingface` |
| `LLM_MODEL` | `mistral` (or `zephyr`, `llama2`) |

**To get HF_API_TOKEN:**
1. Go to https://huggingface.co/settings/tokens
2. Create new token (give it "read" access)
3. Copy the token value
4. Paste in Space secrets

---

## **Step 4: Configure HuggingFace Spaces App**

### 4.1 Update `app.py` for Data Loading
The app will automatically detect HF Spaces and:
- Use HuggingFace Inference API instead of Ollama
- Load data from HF Hub dataset

### 4.2 Create `app.py` Loading Logic
Add to your `app.py` (it's already there):

```python
# Auto-detect HF Spaces
RUNNING_IN_HF_SPACES = os.getenv("SPACE_ID") is not None

if RUNNING_IN_HF_SPACES:
    # Load data from HF Hub
    from tools.embeddings import RAGPipeline
    
    rag = RAGPipeline()
    hf_dataset_repo = os.getenv("HF_DATASET_REPO")
    rag.load_from_hf_hub(hf_dataset_repo)
else:
    # Load from local files
    rag = load_rag_index()
```

---

## **Step 5: Deploy & Test**

### 5.1 Verify Space is Running
1. Go to your Space URL: `https://huggingface.co/spaces/USERNAME/sap-chatbot`
2. Wait for build to complete (~5-10 min first time)
3. Click "Open in iframe" to view the app

### 5.2 Test the System
1. Refresh the page
2. Wait for initialization (10-15 seconds)
3. Type a test query: "How do I monitor SAP jobs?"
4. Verify answer appears with sources

### 5.3 Troubleshooting
- **"HF_API_TOKEN not set"**: Add token to Space secrets
- **"Dataset not found"**: Ensure dataset repo is correct in secrets
- **Slow responses**: First request can be slow (~30-60s), subsequent requests faster

---

## **Step 6: Share Your Space**

Your Space URL: `https://huggingface.co/spaces/USERNAME/sap-chatbot`

### Share with Others:
- ✅ **Public Space** - Anyone can access via URL
- ✅ **Embed** - Add to your website with iframe
- ✅ **Share Badge** - Copy/paste badge to README

---

## **Architecture for HuggingFace Spaces**

```
User Browser
    ↓
Streamlit Cloud (HF Spaces)
    ↓
    ├─→ Load FAISS Index (from HF Hub dataset)
    ├─→ Load Metadata (pickle file)
    └─→ HuggingFace Inference API
         └─→ Generate answers using Mistral/Llama/Zephyr
```

**Total Cost:** 🎉 **FREE!**
- HF Spaces: Free tier
- HF Inference API: Free tier
- HF Hub Storage: Free tier
- Streamlit: No additional cost

---

## **Performance Expectations**

| Metric | Value |
|--------|-------|
| First request | 30-60 seconds (cold start) |
| Subsequent requests | 10-20 seconds |
| Vector search | < 1 second |
| API inference | 10-20 seconds |
| Concurrent users | Up to 5 (free tier) |

---

## **Maintenance & Updates**

### Update Code
```bash
git add .
git commit -m "Update SAP data"
git push origin main
# Space auto-updates!
```

### Update Dataset
```bash
# Rebuild dataset locally
python tools/build_dataset.py

# Rebuild index
python tools/embeddings.py

# Upload to HF Hub
huggingface-cli upload your-username/sap-chatbot-data \
  data/rag_index.faiss data/rag_index.faiss

huggingface-cli upload your-username/sap-chatbot-data \
  data/rag_metadata.pkl data/rag_metadata.pkl
```

---

## **Next Steps**

1. ✅ Create HF Hub account
2. ✅ Upload dataset repo
3. ✅ Push code to GitHub
4. ✅ Create HF Space
5. ✅ Add secrets
6. ✅ Verify deployment
7. ✅ Share URL with SAP community!

---

## **FAQ**

**Q: Can I use local Ollama in HF Spaces?**
A: No, HF Spaces doesn't support running local services. Use HuggingFace Inference API instead.

**Q: What if I hit HF Inference API rate limits?**
A: The free tier has generous limits. For high traffic, upgrade to paid tier or use multiple models.

**Q: How do I make my Space faster?**
A: Upgrade to GPU (paid). For CPU, responses take 10-30 seconds.

**Q: Can I use my own LLM in HF Spaces?**
A: Yes! Use any HuggingFace model with the Inference API or host your own endpoint.

**Q: Is my data private?**
A: Make your dataset repo **Private** in HF Hub. Space data is protected by your HF account.

---

## **Support & Resources**

- 📚 [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- 🚀 [Streamlit Docs](https://docs.streamlit.io)
- 💬 [HuggingFace Community](https://huggingface.co/join-community)
- 🤗 [HF Spaces Examples](https://huggingface.co/spaces)

---

Happy deploying! 🎉
