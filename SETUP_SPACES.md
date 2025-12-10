# 📋 Setup Steps for HuggingFace Spaces Deployment

## Quick Summary
You now have a SAP Chatbot configured for HuggingFace Spaces! Here's exactly what to do:

---

## **Phase 1: Local Preparation (5 minutes)**

### Step 1: Generate HuggingFace API Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `sap-chatbot-spaces`
4. Type: `read` (for reading data and inference)
5. Copy the token value (you'll need this)

### Step 2: Prepare Your Dataset Repository
```bash
# Install HF tools
pip install huggingface-hub

# Login with token
huggingface-cli login
```

Create dataset repo on HuggingFace:
1. Visit https://huggingface.co/datasets
2. Click "New Dataset"
3. Name: `sap-chatbot-data`
4. Visibility: **Private** (recommended)
5. Create repository

### Step 3: Upload Your Data
```bash
cd /Users/akshay/sap-chatboot

# Upload the three crucial files
huggingface-cli upload \
  YOUR-USERNAME/sap-chatbot-data \
  data/rag_index.faiss \
  data/rag_index.faiss

huggingface-cli upload \
  YOUR-USERNAME/sap-chatbot-data \
  data/rag_metadata.pkl \
  data/rag_metadata.pkl

huggingface-cli upload \
  YOUR-USERNAME/sap-chatbot-data \
  data/sap_dataset.json \
  data/sap_dataset.json
```

**Alternative (Easier):**
1. Visit your dataset page: `https://huggingface.co/datasets/YOUR-USERNAME/sap-chatbot-data`
2. Click "Add files" → "Upload files"
3. Drag & drop the three files from `data/` folder

---

## **Phase 2: GitHub Preparation (5 minutes)**

### Step 4: Push Code to GitHub
```bash
cd /Users/akshay/sap-chatboot

# Initialize git repo (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "SAP Chatbot - Initial commit for HF Spaces"

# Create repo on GitHub: https://github.com/new
# Name: sap-chatbot
# Description: Free RAG-based SAP Q&A system

# Add remote and push
git remote add origin https://github.com/YOUR-USERNAME/sap-chatbot.git
git branch -M main
git push -u origin main
```

**What gets pushed:**
- ✅ app.py, config.py, requirements-spaces.txt
- ✅ tools/ folder (agent.py, embeddings.py, build_dataset.py)
- ✅ .streamlit/config.toml
- ✅ DEPLOYMENT_HF_SPACES.md
- ❌ data/ folder (too large, stored on HF Hub)
- ❌ .env (never commit secrets!)

---

## **Phase 3: Create HuggingFace Space (5 minutes)**

### Step 5: Create Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `sap-chatbot`
   - **License**: `Apache 2.0`
   - **Space SDK**: `Streamlit`
   - **Visibility**: `Public` (to share) or `Private`
4. Click "Create Space"

### Step 6: Connect GitHub Repo
1. In Space settings → "Linked Repository"
2. Select your GitHub repo: `sap-chatbot`
3. Space will auto-sync!

**Alternative:** Upload files via git:
```bash
git clone https://huggingface.co/spaces/YOUR-USERNAME/sap-chatbot
cd sap-chatbot
cp -r /Users/akshay/sap-chatboot/* .
git add .
git commit -m "Deploy SAP chatbot"
git push
```

---

## **Phase 4: Configure Secrets (5 minutes)**

### Step 7: Add Environment Secrets

In Space Settings → "Secrets":

| Secret Name | Value | Example |
|-------------|-------|---------|
| `HF_API_TOKEN` | Your HF token from Step 1 | `hf_xR9q...` |
| `HF_DATASET_REPO` | Your dataset repo ID | `your-username/sap-chatbot-data` |
| `LLM_PROVIDER` | `huggingface` | `huggingface` |
| `LLM_MODEL` | `mistral` | `mistral` or `zephyr` |

**How to add:**
1. Click "Settings" in Space header
2. Scroll to "Secrets"
3. For each secret:
   - Name: `HF_API_TOKEN`
   - Value: `hf_xR9q...` (your token)
   - Click "Add secret"

---

## **Phase 5: Deploy & Test (5 minutes)**

### Step 8: Wait for Build
1. Space will automatically build after a few seconds
2. Status shows at bottom: "Building..." → "Running"
3. Building takes 3-10 minutes first time

### Step 9: Test the App
1. Once running, Space shows "Open in iframe"
2. Click to open your chatbot
3. Wait 10-15 seconds for initialization
4. Test with: "How do I monitor SAP background jobs?"
5. You should see an answer with sources!

### Step 10: Share Your Space
Your public URL: 
```
https://huggingface.co/spaces/YOUR-USERNAME/sap-chatbot
```

Share with colleagues!

---

## **Troubleshooting**

### ❌ "HF_API_TOKEN not set"
**Solution:** Add `HF_API_TOKEN` to Space secrets (Phase 4, Step 7)

### ❌ "Dataset not found"
**Solution:** 
- Check `HF_DATASET_REPO` is correct (e.g., `akshay/sap-chatbot-data`)
- Ensure dataset files are uploaded
- Check dataset visibility isn't restricted

### ❌ "Request timed out"
**Solution:** 
- HF Inference API can be slow on first request (30-60s)
- Subsequent requests are faster (10-20s)
- If persistent, upgrade HF account for priority queue

### ❌ Space shows "Building" forever
**Solution:**
- Check Logs: Click "Logs" in Space settings
- Common issues:
  - Missing dependencies: Ensure `requirements-spaces.txt` is correct
  - Wrong Python version: Spaces uses Python 3.10+
  - Import errors: Check `import config` works

### ❌ "No sources returned"
**Solution:**
- Verify RAG index was uploaded correctly
- Test locally: `python tools/embeddings.py`
- Re-upload `rag_index.faiss` and `rag_metadata.pkl`

---

## **Performance Tuning**

### First Request Slow (~30-60s)?
- ✅ Normal! HF Inference API loads model on first use
- Subsequent requests: 10-20s
- Can upgrade for faster inference

### Want Faster Responses?
- 💰 Upgrade HF account for GPU inference
- 📊 Reduce `RAG_TOP_K` in config (fewer context snippets)
- 🔄 Use faster models: `zephyr` instead of `llama2`

### Multiple Users Slow?
- Free tier: ~5 concurrent users
- Paid tier: Scales to 50+ users
- Consider adding caching layer

---

## **What's Included**

### Files Created/Modified:
```
sap-chatbot/
├── app.py                          # Updated for HF Spaces
├── config.py                       # Updated with auto-detection
├── requirements-spaces.txt         # Cloud-optimized dependencies
├── .streamlit/config.toml         # Cloud configuration
├── tools/
│   ├── agent.py                   # Enhanced HF API support
│   └── embeddings.py              # Added HF Hub loading
├── DEPLOYMENT_HF_SPACES.md        # Detailed deployment guide
└── SETUP_SPACES.md               # This file
```

### What's Different for Cloud?
1. **LLM Provider**: Uses HuggingFace Inference API (not Ollama)
2. **Data Loading**: Streams from HF Hub (not local)
3. **Dependencies**: Lighter (no Ollama, Replicate libs)
4. **Auto-detection**: Detects when running in HF Spaces

---

## **After Deployment - Next Steps**

### ✅ It's Live! Now What?
1. Share the URL with your SAP team
2. Gather feedback
3. Iterate on the dataset (add more docs)
4. Monitor usage

### 📈 Improve Your Chatbot
- Add more SAP docs: Edit `tools/build_dataset.py`
- Rebuild dataset locally
- Re-upload to HF Hub
- Space auto-updates!

### 🔍 Monitor Performance
- Check Space Logs for errors
- Monitor HF API usage
- Track response times
- Get feedback from users

---

## **Complete Command Reference**

```bash
# Local setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test locally
streamlit run app.py

# Prepare data
python tools/build_dataset.py
python tools/embeddings.py

# Upload to HF Hub
huggingface-cli upload YOUR-USERNAME/sap-chatbot-data \
  data/rag_index.faiss data/rag_index.faiss

# Push to GitHub
git add .
git commit -m "Deploy to HF Spaces"
git push origin main

# Space auto-deploys!
```

---

## **Cost Breakdown**

| Component | Cost |
|-----------|------|
| HF Spaces (Streamlit) | Free tier |
| HF Dataset (Storage) | Free tier |
| HF Inference API | Free tier (limited) |
| GitHub (Repo) | Free |
| **Total Monthly** | **$0** 🎉 |

---

## **Questions?**

Refer to:
- 📚 [DEPLOYMENT_HF_SPACES.md](./DEPLOYMENT_HF_SPACES.md) - Detailed guide
- 🚀 [README.md](./README.md) - Project overview
- 💬 [HuggingFace Community](https://huggingface.co/join-community)

---

**You're all set! Your SAP Chatbot will be available at:**
```
https://huggingface.co/spaces/YOUR-USERNAME/sap-chatbot
```

Happy chatting! 🤖
