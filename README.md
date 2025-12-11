---
title: SAP Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 🧩 SAP Intelligent Assistant

A free, open-source **RAG (Retrieval-Augmented Generation)** system for answering SAP-related questions using cloud LLMs and vector databases.

## ✨ Key Features

- ✅ 100% Free & Open Source
- ✅ Multi-source SAP data (Community, GitHub, StackOverflow, Dev.to, Medium)
- ✅ Production-ready: Supabase + pgvector vector database
- ✅ HuggingFace Inference API for fast responses
- ✅ Automatic data ingestion via GitHub Actions
- ✅ Beautiful Streamlit UI
- ✅ Multi-user cloud hosting
- ✅ Conversation history with source attribution

## 🚀 How It Works

```
1. Data Collection → 2. Embeddings → 3. Vector Search → 4. Answer Generation
   (SAP sources)       (sentence-         (Supabase        (HF Inference
                       transformers)      pgvector)        API)
```

**Supported Topics:**
- SAP Basis Administration
- SAP ABAP Development  
- SAP HANA
- SAP Fiori & UI5
- SAP Security & Authorization
- SAP BTP (Business Technology Platform)
- SAP Integration Suite
- SAP Performance Tuning
- And more!

## 🔧 Setup

### 1. Local Development (with Ollama)

```bash
# Clone repo
git clone https://github.com/Akshay-S-PY/sap-chatboot
cd sap-chatboot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build dataset
python tools/build_dataset.py

# Run locally
streamlit run app.py
```

### 2. Production (Supabase + HF Spaces)

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for step-by-step cloud deployment.

## 📊 Architecture

```
GitHub Repository (sap-chatboot)
        ↓
GitHub Actions Workflows:
  1. build_dataset.yml → Dataset + Upload to HF Hub
  2. ingest.yml → Ingest to Supabase
  3. deploy_spaces.yml → Deploy to HF Spaces
        ↓
Supabase Database (pgvector + RLS)
        ↓
Streamlit App (HF Spaces)
        ↓
User Query → Vector Search → LLM Response + Sources
```

## 📚 Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Vector Database | Supabase (pgvector) | Free |
| Embeddings | sentence-transformers | Free |
| LLM API | HuggingFace Inference | Free |
| App Hosting | HF Spaces | Free |
| Data Pipeline | GitHub Actions | Free |

## 💡 Use Cases

- **Quick SAP Questions**: Get instant answers about SAP config, ABAP, Basis
- **Learning**: Understand SAP concepts with cited sources
- **Team Knowledge Base**: Share with your entire team
- **Integration**: Use programmatically via Python API

## 🔗 Resources

- 📖 [GitHub Repository](https://github.com/Akshay-S-PY/sap-chatboot)
- 🔗 [Supabase](https://supabase.com)
- 🤗 [HuggingFace](https://huggingface.co)
- 💬 [SAP Community](https://community.sap.com)

## ⚠️ Important Notes

- First run builds dataset (~5-10 min)
- Works 100% offline with Ollama
- All data sources are publicly available and respectfully scraped
- No personal data is stored

---

**Made with ❤️ for the SAP Community**

Have questions? Check the [documentation](./SUPABASE_SETUP.md) or create an [issue](https://github.com/Akshay-S-PY/sap-chatboot/issues).
