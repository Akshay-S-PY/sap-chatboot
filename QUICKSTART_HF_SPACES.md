# 🚀 QUICK START: Deploy to HuggingFace Spaces

**TL;DR - Get your SAP Chatbot live in 30 minutes, for FREE!**

---

## Step 1: Get Your HF Token (2 min)
```bash
# Go to: https://huggingface.co/settings/tokens
# Click "New token"
# Name: sap-chatbot
# Type: read
# Copy the token
```

---

## Step 2: Upload Your Data (5 min)
```bash
# Install HF tools
pip install huggingface-hub

# Login
huggingface-cli login
# Paste your token

# Create dataset on: https://huggingface.co/datasets
# Name it: sap-chatbot-data
# Set to: Private

# Upload files (replace YOUR-USERNAME)
huggingface-cli upload YOUR-USERNAME/sap-chatbot-data \
  data/rag_index.faiss data/rag_index.faiss

huggingface-cli upload YOUR-USERNAME/sap-chatbot-data \
  data/rag_metadata.pkl data/rag_metadata.pkl

huggingface-cli upload YOUR-USERNAME/sap-chatbot-data \
  data/sap_dataset.json data/sap_dataset.json
```

---

## Step 3: Push Code to GitHub (5 min)
```bash
cd /Users/akshay/sap-chatboot

git init
git add .
git commit -m "SAP Chatbot - Ready for HF Spaces"

# Create repo on github.com first, then:
git remote add origin https://github.com/YOUR-USERNAME/sap-chatbot.git
git branch -M main
git push -u origin main
```

---

## Step 4: Create HF Space (5 min)
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Name:** sap-chatbot
   - **SDK:** Streamlit
   - **Visibility:** Public
4. Click "Create Space"

---

## Step 5: Connect GitHub (5 min)
1. In Space: Settings → "Linked Repository"
2. Select your GitHub repo
3. Space auto-syncs with GitHub!

---

## Step 6: Add Secrets (5 min)
In Space Settings → "Secrets" add:

```
HF_API_TOKEN = hf_xR9q... (your token from Step 1)
HF_DATASET_REPO = YOUR-USERNAME/sap-chatbot-data
LLM_PROVIDER = huggingface
LLM_MODEL = mistral
```

---

## Step 7: Done! 🎉
- Space auto-builds (~5 min)
- Once ready, click "Open in iframe"
- Test with: "How do I monitor SAP jobs?"
- Share your URL with colleagues!

---

## Your Public URL
```
https://huggingface.co/spaces/YOUR-USERNAME/sap-chatbot
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "HF_API_TOKEN not set" | Add to secrets (Step 6) |
| "Dataset not found" | Check repo name matches Step 6 |
| "Build failed" | Check Space Logs |
| "Slow responses" | Normal on free tier (10-30s) |

---

## Need More Help?

- **Detailed Setup:** See `SETUP_SPACES.md`
- **Full Guide:** See `DEPLOYMENT_HF_SPACES.md`
- **Overview:** See `HF_SPACES_COMPLETE.md`

---

**That's it! Your chatbot is live. Enjoy! 🚀**
