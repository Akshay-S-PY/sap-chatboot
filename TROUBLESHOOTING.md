# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. Setup Issues

#### "ModuleNotFoundError: No module named 'streamlit'"
**Problem**: Dependencies not installed
**Solution**:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

#### "python3: command not found"
**Problem**: Python not installed or not in PATH
**Solution**:
```bash
# Install Python 3.8+
# macOS: brew install python3
# Ubuntu/Debian: sudo apt install python3
# Windows: Download from python.org

# Verify:
python3 --version
```

#### "virtualenv not found"
**Problem**: venv module missing
**Solution**:
```bash
# Install it:
# macOS: brew install python3-venv
# Ubuntu: sudo apt install python3-venv
# Then recreate venv:
python3 -m venv .venv
```

---

### 2. Dataset Building Issues

#### "No article URLs found"
**Problem**: Website structure changed or connection failed
**Solution**:
```bash
# Check internet connection
ping community.sap.com

# Try rebuilding with debug
python tools/build_dataset.py

# Check if data directory exists
ls -la data/
```

#### "Connection timeout"
**Problem**: Website taking too long to respond
**Solution**:
```bash
# Modify timeout in tools/build_dataset.py:
# Change: timeout=10
# To: timeout=30

# Or add delay
import time
time.sleep(5)  # Between requests
```

#### "Permission denied" error
**Problem**: Can't write to data directory
**Solution**:
```bash
# Fix permissions
mkdir -p data
chmod 755 data/

# Or run with sudo (not recommended)
sudo python tools/build_dataset.py
```

---

### 3. Embeddings/Index Issues

#### "ModuleNotFoundError: No module named 'faiss'"
**Problem**: FAISS not installed correctly
**Solution**:
```bash
pip uninstall faiss-cpu
pip install faiss-cpu --no-cache-dir

# Or use GPU version if available:
# pip install faiss-gpu
```

#### "CUDA error" / "GPU not found"
**Problem**: GPU version installed but no GPU available
**Solution**:
```bash
# Use CPU version instead
pip uninstall faiss-gpu
pip install faiss-cpu
```

#### "MemoryError during embeddings"
**Problem**: System ran out of memory
**Solution**:
```python
# In tools/embeddings.py, reduce batch size:
# Change: batch_size=32
# To: batch_size=8 or 4

# Or use smaller model:
# Change: model_name="all-MiniLM-L6-v2"
# To: model_name="sentence-transformers/all-MiniLM-L12-v2"
```

#### "Index not found" error
**Problem**: RAG index not built
**Solution**:
```bash
# Rebuild the index
python tools/embeddings.py

# Verify files exist
ls -la data/rag_index.faiss
ls -la data/rag_metadata.pkl
```

---

### 4. LLM Provider Issues

#### Ollama

**"ConnectionRefusedError: [Errno 111] Connection refused"**
```bash
# Ollama server not running
# Start it in a new terminal:
ollama serve

# Or use nohup to background it:
nohup ollama serve &
```

**"Model not found"**
```bash
# Pull the model first:
ollama pull mistral
# Or
ollama pull neural-chat
ollama pull dolphin-mixtral

# List available models:
ollama list
```

**"Out of memory"**
```bash
# Use smaller model:
ollama pull neural-chat  # 3B instead of 7B

# Or configure in config.py:
DEFAULT_MODEL = "neural-chat"
```

#### Replicate

**"REPLICATE_API_TOKEN not set"**
```bash
# Set token in terminal:
export REPLICATE_API_TOKEN="your_token_here"

# Or add to .env:
REPLICATE_API_TOKEN=your_token_here

# Verify:
echo $REPLICATE_API_TOKEN
```

**"401 Unauthorized"**
```bash
# Token is invalid or expired
# 1. Get new token from https://replicate.com/account
# 2. Update environment variable
# 3. Try again
```

**"Rate limit exceeded"**
```bash
# Wait a bit, then try again
# Or use Ollama/HuggingFace instead
```

#### HuggingFace

**"HF_API_TOKEN not set"**
```bash
# Set token:
export HF_API_TOKEN="your_token_here"

# Or add to .env:
HF_API_TOKEN=your_token_here

# Verify:
echo $HF_API_TOKEN
```

**"Model not found" on HuggingFace**
```bash
# Verify model ID exists:
# Go to https://huggingface.co/models
# Find a text-generation model
# Example: mistralai/Mistral-7B-Instruct-v0.1

# Update config:
LLM_MODEL="mistralai/Mistral-7B-Instruct-v0.1"
```

---

### 5. Streamlit Issues

#### "streamlit: command not found"
**Problem**: Streamlit not installed
**Solution**:
```bash
source .venv/bin/activate
pip install streamlit>=1.28.0
```

#### Port 8501 already in use
**Problem**: Another app using port 8501
**Solution**:
```bash
# Use different port:
streamlit run app.py --server.port 8502

# Or kill the process using 8501:
lsof -i :8501  # See what's using it
kill -9 <PID>  # Kill it
```

#### "Cache resource initialization failed"
**Problem**: Session state issue
**Solution**:
```bash
# Clear Streamlit cache:
rm -rf ~/.streamlit/cache/

# Restart the app:
streamlit run app.py
```

#### App not responding / frozen
**Problem**: Long-running operation blocking UI
**Solution**:
```bash
# Wait for current operation to complete
# Or restart:
# 1. Press Ctrl+C
# 2. Run: streamlit run app.py again
```

---

### 6. Runtime Issues

#### "Empty search results"
**Problem**: No relevant documents found
**Solution**:
```bash
# 1. Verify dataset exists:
ls -la data/sap_dataset.json

# 2. Verify index exists:
ls -la data/rag_index.faiss

# 3. Try a different query:
# "SAP Basis administration" instead of "help"

# 4. Rebuild dataset:
python tools/build_dataset.py
python tools/embeddings.py
```

#### "Very slow responses"
**Problem**: LLM taking too long
**Solution**:
```python
# Use faster model in config.py:
DEFAULT_MODEL = "neural-chat"  # 3B is 2-3x faster

# Or use cloud provider (usually faster):
LLM_PROVIDER = "replicate"
```

#### "Inaccurate or irrelevant answers"
**Problem**: RAG not finding good sources or LLM quality
**Solution**:
```python
# 1. Improve RAG:
# In config.py, increase sources:
RAG_TOP_K = 10  # From 5

# 2. Use better embeddings:
EMBEDDINGS_MODEL = "all-mpnet-base-v2"  # Better quality

# 3. Use better LLM:
DEFAULT_MODEL = "mistral"  # From neural-chat

# 4. Rebuild index:
python tools/embeddings.py
```

#### "API rate limit exceeded"
**Problem**: Using cloud provider too frequently
**Solution**:
```bash
# 1. Wait a bit
# 2. Use Ollama (no rate limits)
# 3. Or try different cloud provider
```

---

### 7. Configuration Issues

#### "Settings not taking effect"
**Problem**: Configuration changes not applied
**Solution**:
```bash
# 1. Make sure you edited the right file:
cat .env

# 2. Restart the app:
# Ctrl+C and run again

# 3. Clear cache:
rm -rf ~/.streamlit/cache/
streamlit run app.py
```

#### "Environment variables not loading"
**Problem**: .env file not being read
**Solution**:
```python
# Verify in app.py or config.py:
# from dotenv import load_dotenv
# load_dotenv()  # Must be called

# Or set manually:
export VAR_NAME="value"
streamlit run app.py
```

---

### 8. Performance Issues

#### "High CPU usage"
**Problem**: Embeddings or search consuming CPU
**Solution**:
```python
# Use batch processing in embeddings.py:
# Already optimized with batch_size=32

# Or use pre-built index (don't rebuild often)
```

#### "High memory usage"
**Problem**: Large dataset or model in memory
**Solution**:
```python
# Use lighter model in config.py:
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"

# Reduce chunk size:
RAG_CHUNK_SIZE = 256  # From 512

# Use Ollama 3B model:
ollama pull neural-chat
```

#### "Slow search"
**Problem**: FAISS search taking too long
**Solution**:
```python
# Should be fast already, but:

# 1. Reduce results:
RAG_TOP_K = 3  # From 5

# 2. Check if index is corrupted:
# Rebuild it:
python tools/embeddings.py
```

---

### 9. Deployment Issues

#### Streamlit Cloud deployment fails
**Problem**: Missing secrets or dependencies
**Solution**:
```bash
# 1. Add secrets in Streamlit Cloud:
# Settings → Secrets
# LLM_PROVIDER=replicate
# REPLICATE_API_TOKEN=xxx

# 2. Make sure requirements.txt is in repo
# 3. Commit data files or download on deploy

# 4. Check build logs:
# Deploy → Manage app → Logs
```

#### Docker container issues
**Problem**: Can't build or run Docker image
**Solution**:
```bash
# Create Dockerfile (if not exists)
# Build: docker build -t sap-chatbot .
# Run: docker run -p 8501:8501 sap-chatbot

# Or provide Docker guide
```

---

### 10. Data Issues

#### "Dataset is outdated"
**Problem**: Knowledge base needs refresh
**Solution**:
```bash
# Rebuild dataset:
rm data/sap_dataset.json
python tools/build_dataset.py
python tools/embeddings.py

# Takes 10-15 minutes but gets latest content
```

#### "Too much data (slow startup)"
**Problem**: Large dataset causing slow startup
**Solution**:
```python
# Limit dataset in build_dataset.py:
# Change: for repo in repos (all repos)
# To: for repo in repos[:10] (first 10 only)

# Or reduce sources scraped
```

#### "Data format error"
**Problem**: JSON file corrupted
**Solution**:
```bash
# Verify JSON:
python -c "import json; json.load(open('data/sap_dataset.json'))"

# If error, rebuild:
rm data/sap_dataset.json
python tools/build_dataset.py
```

---

## Quick Diagnosis

### System Check Script

```bash
#!/bin/bash
echo "SAP Chatbot System Check"
echo "========================"
echo ""

echo "1. Python:"
python3 --version

echo ""
echo "2. Virtual Environment:"
if [ -d ".venv" ]; then
    echo "✅ Exists"
else
    echo "❌ Missing"
fi

echo ""
echo "3. Dependencies:"
pip list | grep -E "streamlit|transformers|faiss|ollama"

echo ""
echo "4. Dataset:"
ls -lh data/sap_dataset.json 2>/dev/null || echo "❌ Not found"

echo ""
echo "5. Index:"
ls -lh data/rag_index.faiss 2>/dev/null || echo "❌ Not found"

echo ""
echo "6. .env file:"
[ -f ".env" ] && echo "✅ Exists" || echo "❌ Missing"

echo ""
echo "7. Ollama:"
curl -s http://localhost:11434/ > /dev/null && echo "✅ Running" || echo "❌ Not running"

echo ""
echo "Check complete!"
```

Save as `check_system.sh` and run:
```bash
bash check_system.sh
```

---

## Getting Help

1. **Check this guide** - Most issues documented
2. **Read GETTING_STARTED.md** - Step-by-step setup
3. **Check README.md** - Architecture & concepts
4. **Check config.py** - All configuration options
5. **Look at code** - Well-commented Python files
6. **Open GitHub issue** - Report bugs with details

---

## Debug Mode

Enable debug logging:

```python
# In app.py or any module:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message here")
```

Then run:
```bash
streamlit run app.py --logger.level=debug
```

---

**Still stuck?** Check the GitHub issues or create a new one with:
- Python version
- OS (Windows/Mac/Linux)
- Error message (full traceback)
- Steps to reproduce
- What you've already tried

Good luck! 🚀
