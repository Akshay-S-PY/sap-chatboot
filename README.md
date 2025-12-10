# 🧩 SAP Intelligent Assistant

A free, open-source **RAG (Retrieval-Augmented Generation)** system for answering SAP-related questions using cloud LLMs and vector databases.

**Key Features:**
- ✅ 100% Free & Open Source (with paid options)
- ✅ Multi-source SAP data (Community, GitHub, StackOverflow, blogs)
- ✅ **Production-ready**: Supabase + pgvector for vector search
- ✅ HuggingFace Inference API for embeddings & generation
- ✅ Automatic ingestion via GitHub Actions
- ✅ Beautiful Streamlit UI
- ✅ Multi-user cloud hosting on HuggingFace Spaces
- ✅ Conversation history & source tracking

---

## 🚀 Architecture

```
Documents → GitHub → GitHub Actions → Supabase (pgvector)
                         ↓
                     ingest.py
                   (embeddings)
                              ↓
                         Users → HF Spaces
                              ↓
                          Streamlit App
                         (HF Inference API)
                              ↓
                    Vector Search (Supabase RPC)
                              ↓
                        Answer Generation
```

---

## 🌐 Deploy to HuggingFace Spaces

**Share your chatbot with your entire team - for FREE!**

### Quick Start (Production Setup)

👉 **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** ← Start here for cloud deployment

### Alternative: Local Setup (Offline)

Or follow: **[QUICKSTART_HF_SPACES.md](./QUICKSTART_HF_SPACES.md)**

**What you get:**
- ✅ Production database (Supabase pgvector)
- ✅ Automatic ingestion (GitHub Actions)
- ✅ Multi-user access (5+ concurrent)
- ✅ Zero cost (free tier)
- ✅ Auto-scaling infrastructure

---

### Option 1: Local (Offline) Setup with Ollama

**1. Install Ollama**
```bash
# Download from https://ollama.ai
# Then start the server
ollama serve
```

**2. Pull an LLM model**
```bash
# Fast option (3B)
ollama pull neural-chat

# Or balanced (7B)
ollama pull mistral

# Or best quality (8x7B)
ollama pull dolphin-mixtral
```

**3. Setup SAP Assistant**
```bash
# Clone/setup the project
cd /Users/akshay/sap-chatboot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Build dataset from web
python tools/build_dataset.py

# Build vector index
python tools/embeddings.py

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser!

### Option 2: Cloud Setup (Replicate Free Tier)

**1. Get API Token**
- Sign up free at https://replicate.com
- Get your API token

**2. Setup**
```bash
cd sap-chatboot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export REPLICATE_API_TOKEN="your_token_here"
python tools/build_dataset.py
python tools/embeddings.py

export LLM_PROVIDER=replicate
export LLM_MODEL=meta/llama-2-7b-chat
streamlit run app.py
```

### Option 3: HuggingFace Free Tier

**1. Get API Token**
- Create account at https://huggingface.co
- Get token from https://huggingface.co/settings/tokens

**2. Setup**
```bash
cd sap-chatboot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export HF_API_TOKEN="your_token_here"
python tools/build_dataset.py
python tools/embeddings.py

export LLM_PROVIDER=huggingface
export LLM_MODEL="mistralai/Mistral-7B-Instruct-v0.1"
streamlit run app.py
```

## 📊 Architecture

```
Web Scraper (build_dataset.py)
├── SAP Community
├── GitHub Repos
├── Dev.to
└── Tech Blogs
        ↓
    SAP Dataset (sap_dataset.json)
        ↓
RAG Pipeline (embeddings.py)
├── Chunk Management
├── Embeddings (Sentence Transformers)
└── FAISS Vector Index
        ↓
    Vector Index (rag_index.faiss)
        ↓
LLM Agent (agent.py)
├── Ollama (Local)
├── Replicate (Free)
└── HuggingFace (Free)
        ↓
    Streamlit UI (app.py)
    ├── Chat Interface
    └── Source Attribution
```

## 📁 Project Structure

```
sap-chatboot/
├── app.py                      # Main Streamlit UI
├── config.py                   # Configuration & prompts
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
│
├── tools/
│   ├── build_dataset.py        # Web scraper for SAP data
│   ├── embeddings.py           # RAG pipeline & vector store
│   └── agent.py                # LLM agent with multiple providers
│
└── data/
    ├── sap_dataset.json        # Scraped SAP knowledge base
    ├── rag_index.faiss         # Vector index
    └── rag_metadata.pkl        # Chunk metadata
```

## 🔧 Configuration

Create `.env` file (copy from `.env.example`):

```env
# LLM Provider: ollama, replicate, or huggingface
LLM_PROVIDER=ollama
LLM_MODEL=mistral

# API Tokens (if using cloud providers)
REPLICATE_API_TOKEN=your_token
HF_API_TOKEN=your_token

# Embeddings model
EMBEDDINGS_MODEL=all-MiniLM-L6-v2

# RAG settings
RAG_TOP_K=5
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=100
```

## 📚 Available LLMs

### Ollama (Local - Free)
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| Neural Chat | 3B | ⚡⚡⚡ | Good |
| Mistral | 7B | ⚡⚡ | Excellent |
| Dolphin Mixtral | 8x7B | ⚡ | Best |

### Replicate (Free Tier)
- Llama 2 7B
- Mistral 7B
- And more open models

### HuggingFace (Free Tier)
- Any HuggingFace text-generation model

## 🔍 How It Works

1. **Data Collection** (`build_dataset.py`)
    - Scrapes SAP Community, StackOverflow, GitHub, dev.to, Medium, SAP Developers tutorials
   - Saves structured JSON

2. **Embeddings & Indexing** (`embeddings.py`)
   - Splits documents into chunks
   - Generates embeddings (Sentence Transformers)
   - Builds FAISS vector index

3. **Query & Answer** (`agent.py`)
   - User asks question
   - RAG retrieves relevant documents
   - LLM generates answer with context
   - Sources attributed

## 💡 Supported Topics

✅ SAP Basis Administration
✅ SAP ABAP Development
✅ SAP HANA
✅ SAP Fiori & UI5
✅ SAP Security & Authorization
✅ SAP Configuration
✅ SAP Performance Tuning
✅ And more!

## 🚀 Deployment

### Deploy on Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Select your repository
4. Add environment secrets
5. Deploy!

### Deploy on Your Server

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

## 🛠️ Advanced Usage

### Programmatic Access

```python
from tools.embeddings import load_rag_index
from tools.agent import SAPAgent, SAGAAssistant

rag = load_rag_index()
agent = SAPAgent(llm_provider="ollama", model="mistral")
assistant = SAGAAssistant(rag_pipeline=rag, llm_agent=agent)

response = assistant.answer("How to backup SAP database?")
print(response['answer'])
print(response['sources'])
```

## ⚠️ Important Notes

- **First Run**: Building dataset takes 5-10 minutes
- **Storage**: Dataset ~100MB-500MB depending on sources
- **Internet**: Only needed for initial scraping
- **Local Mode**: Works 100% offline with Ollama
- **Rate Limits**: Web scraper is respectful

## 📊 Performance Tips

| Goal | Setting |
|------|---------|
| **Fastest** | neural-chat + MiniLM |
| **Best Quality** | dolphin-mixtral + mpnet |
| **Memory Efficient** | MiniLM + small model |
| **Cloud Friendly** | Replicate or HuggingFace |

## ❓ FAQ

**Q: Is this really free?**
A: Yes! All components are free and open-source.

**Q: Can I use offline?**
A: Yes! Use Ollama for completely offline operation.

**Q: How accurate?**
A: RAG provides sources so you can verify.

**Q: Can I add custom data?**
A: Yes! Edit `build_dataset.py` to add sources.

**Q: Privacy?**
A: Local mode: All on your machine.

## 🔗 Resources

- **Ollama**: https://ollama.ai
- **Replicate**: https://replicate.com
- **HuggingFace**: https://huggingface.co
- **SAP Community**: https://community.sap.com

---

**Made with ❤️ for the SAP Community**

**Star ⭐ if you find this useful!**
