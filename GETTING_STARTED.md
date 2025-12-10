# GETTING_STARTED.md

## 🚀 Getting Started with SAP Intelligent Assistant

This guide will help you get the SAP Chatbot running in less than 30 minutes.

## Prerequisites

- **Python 3.8+** - Check with: `python3 --version`
- **Internet Connection** - For initial setup and data collection
- **~2GB Storage** - For dataset and models

## Step 1: Clone & Initial Setup (5 minutes)

```bash
# Navigate to your workspace
cd /Users/akshay/sap-chatboot

# Run setup script (handles everything)
bash setup.sh

# Or manual setup:
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file
cp .env.example .env
```

## Step 2: Choose Your LLM Option

### Option A: Ollama (Recommended for Offline)

**Best for:** Local development, offline usage, privacy

```bash
# 1. Install Ollama from https://ollama.ai

# 2. Start Ollama server (in a separate terminal)
ollama serve

# 3. Pull a model (in another terminal)
# Pick one:
ollama pull neural-chat      # Fast (3B)
ollama pull mistral          # Balanced (7B)
ollama pull dolphin-mixtral  # Best quality (8x7B)

# 4. Update .env
LLM_PROVIDER=ollama
LLM_MODEL=mistral
```

### Option B: Replicate (Easiest Cloud Option)

**Best for:** Cloud deployment, zero local setup

```bash
# 1. Sign up free at https://replicate.com
# 2. Get your API token

# 3. Set environment variable
export REPLICATE_API_TOKEN="your_token_here"

# 4. Update .env
LLM_PROVIDER=replicate
LLM_MODEL=meta/llama-2-7b-chat
```

### Option C: HuggingFace (Most Flexibility)

**Best for:** Testing different models easily

```bash
# 1. Sign up at https://huggingface.co
# 2. Get token from https://huggingface.co/settings/tokens

# 3. Set environment variable
export HF_API_TOKEN="your_token_here"

# 4. Update .env
LLM_PROVIDER=huggingface
LLM_MODEL="mistralai/Mistral-7B-Instruct-v0.1"
```

## Step 3: Build the Knowledge Base (10 minutes)

```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Build SAP dataset from web sources
# This scrapes: SAP Community, GitHub, Dev.to, etc.
python tools/build_dataset.py

# This creates: data/sap_dataset.json
```

## Step 4: Build the Vector Index (5 minutes)

```bash
# Create embeddings and FAISS vector index
python tools/embeddings.py

# This creates:
# - data/rag_index.faiss
# - data/rag_metadata.pkl
```

## Step 5: Run the App (2 minutes)

```bash
# Option 1: Quick start (automatic)
python quick_start.py

# Option 2: Manual
streamlit run app.py

# The app opens at: http://localhost:8501
```

## Troubleshooting

### "Ollama not running"
```bash
# In a separate terminal:
ollama serve
```

### "REPLICATE_API_TOKEN not set"
```bash
export REPLICATE_API_TOKEN="your_token"
# Or add to .env file
```

### "No such file: sap_dataset.json"
```bash
# Rebuild dataset
python tools/build_dataset.py
python tools/embeddings.py
```

### "Memory error"
```bash
# Use lighter embeddings model in config.py:
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # Already default (light)

# Or use faster LLM:
ollama pull neural-chat  # 3B instead of 7B
```

### "Very slow responses"
```bash
# For faster responses, use:
LLM_MODEL=neural-chat  # 3B is 2-3x faster

# Or use cloud provider:
# Replicate or HuggingFace (but need API token)
```

## Quick Test

Once running, try these questions:

1. **"How do I monitor background jobs in SAP?"**
   - Tests: Data retrieval, LLM quality

2. **"What is SAP Basis?"**
   - Tests: General knowledge

3. **"How to debug ABAP programs?"**
   - Tests: Developer knowledge

## Next Steps

### After First Run

1. **Customize the dataset:**
   - Edit `tools/build_dataset.py`
   - Add your own SAP documentation URLs

2. **Deploy to cloud:**
   - Push to GitHub
   - Deploy on Streamlit Cloud
   - See README.md for details

3. **Fine-tune performance:**
   - Adjust `RAG_TOP_K` in config.py
   - Change embeddings model
   - Optimize chunk size

### Development

```bash
# Run in development mode
streamlit run app.py --logger.level=debug

# Check logs
tail -f logs/app.log
```

## Architecture Summary

```
Your Question
    ↓
Vector Search (FAISS)
    ↓
Top 5 Similar Chunks
    ↓
LLM (Ollama/Replicate/HF)
    ↓
Answer + Sources
```

## Configuration Tips

| Use Case | Setting |
|----------|---------|
| **Fastest** | neural-chat + all-MiniLM-L6-v2 |
| **Best Quality** | mistral + all-mpnet-base-v2 |
| **Offline** | Ollama + any model |
| **Cloud** | Replicate + Mistral |
| **Low Memory** | Keep current settings |

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Slow on first run | Building dataset is normal, takes 5-10 min |
| Timeout errors | Increase timeout in `tools/build_dataset.py` |
| Empty responses | Check if dataset was built successfully |
| Memory errors | Use smaller model or embeddings |
| API errors | Check token and internet connection |

## Getting Help

1. **Check README.md** - Comprehensive documentation
2. **FAQ Section** - Common questions answered
3. **GitHub Issues** - Report bugs
4. **Configuration** - See `config.py` for all options

## What's Next?

- ✅ Your system is ready!
- 📚 Start asking SAP questions
- 🚀 Deploy when comfortable
- 📖 Read README.md for advanced usage

---

**Happy learning! 🧩**

For more details, see README.md
