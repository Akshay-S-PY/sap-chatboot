# 📁 Project Files Overview

## Root Level Files

### Application Core
- **app.py** (13KB)
  - Main Streamlit UI application
  - Chat interface with source display
  - Session management
  - System initialization

### Configuration
- **config.py** (5KB)
  - Central configuration management
  - LLM provider settings
  - RAG parameters
  - System prompts
  - Help messages

### Environment
- **.env.example** (1KB)
  - Configuration template
  - API token placeholders
  - Model selection options
  - Copy to .env to use

- **.gitignore**
  - Virtual environment exclusion
  - Data files
  - Cache & IDE settings
  - Logs & temporary files

### Setup & Launch
- **setup.sh** (1.2KB)
  - Automated environment setup
  - Dependency installation
  - Directory creation
  - Executable: bash setup.sh

- **quick_start.py** (1.7KB)
  - One-click launcher
  - Auto-builds dataset if needed
  - Auto-builds index if needed
  - Executable: python quick_start.py

### Dependencies
- **requirements.txt** (664B)
  - Python package list
  - Streaming, AI/ML, web scraping
  - LLM provider libraries
  - Utility packages
  - All free & open-source

---

## Tools Directory (tools/)

### Web Scraper
- **build_dataset.py** (8.7KB)
  - SAPDatasetBuilder class
  - Multi-source scraping:
    - SAP Community blogs
    - GitHub repositories
    - Dev.to articles
    - Generic webpages
  - Features:
    - Rate limiting
    - Error handling
    - Deduplication
    - JSON output

### RAG Pipeline
- **embeddings.py** (7.1KB)
  - RAGPipeline class
  - Sentence Transformers embeddings
  - FAISS vector search
  - Chunk management
  - Index save/load
  - Standalone functions:
    - build_rag_index()
    - load_rag_index()

### LLM Agent
- **agent.py** (8.7KB)
  - SAPAgent class (multiple LLM support)
  - SAGAAssistant class (RAG + LLM)
  - Provider implementations:
    - Ollama (local)
    - Replicate (free cloud)
    - HuggingFace (free cloud)
  - Features:
    - Conversation history
    - System prompts
    - Response formatting
    - Error handling

### Other
- **upload_to_hf.py** (2.2KB)
  - Upload dataset to HuggingFace Hub
  - For cloud storage of large datasets

---

## Documentation Files

### Getting Started
- **GETTING_STARTED.md** (5.3KB)
  - Prerequisites checklist
  - 5-step setup process
  - 3 LLM installation options
  - Troubleshooting table
  - Quick test queries
  - Configuration tips

### Main Documentation
- **README.md** (7KB)
  - Project overview
  - Quick start (3 options)
  - Complete architecture diagram
  - Project structure explanation
  - Configuration guide
  - Available LLMs table
  - How it works explanation
  - Supported topics
  - Deployment options
  - Advanced usage examples
  - FAQ section
  - Resource links

### Troubleshooting
- **TROUBLESHOOTING.md** (10.6KB)
  - 10 categories of issues
  - Setup issues (3 problems)
  - Dataset issues (3 problems)
  - Embeddings issues (4 problems)
  - LLM provider issues (9 problems)
  - Streamlit issues (4 problems)
  - Runtime issues (3 problems)
  - Configuration issues (2 problems)
  - Performance issues (3 problems)
  - Deployment issues (2 problems)
  - Data issues (3 problems)
  - Quick diagnosis script
  - Debug mode instructions

### Implementation Summary
- **IMPLEMENTATION_SUMMARY.md** (8KB)
  - What has been created
  - Component breakdown
  - Architecture diagram
  - Key features list
  - How to use
  - Data flow explanation
  - Supported SAP topics
  - File statistics
  - What makes it special

### Project Checklist
- **PROJECT_CHECKLIST.md** (6KB)
  - Complete feature checklist
  - Statistics & metrics
  - Architecture overview
  - Customization points
  - Getting started reference
  - Deployment checklist
  - Documentation quality
  - Learning resources
  - What you can do now
  - Next steps

---

## Data Directory (data/)
*Created at runtime*

- **sap_dataset.json**
  - Scraped SAP knowledge base
  - ~1000+ documents
  - Structured JSON format

- **rag_index.faiss**
  - FAISS vector index
  - Fast similarity search
  - ~100MB+ size

- **rag_metadata.pkl**
  - Chunk metadata
  - Document references
  - Source attribution

- **raw/**
  - Raw scraped content
  - Temporary processing files

---

## Hidden Files

- **.env** (not in git)
  - Your actual configuration
  - API tokens
  - Model selections
  - Create from .env.example

- **.venv/** (not in git)
  - Virtual environment
  - Installed packages
  - Python interpreter

- **.streamlit/cache/** (not in git)
  - Streamlit cache
  - Session state

- **.github/workflows/** (in git if exists)
  - GitHub Actions
  - CI/CD pipeline

---

## File Organization

```
sap-chatboot/
├── Core Application
│   ├── app.py                 ← Main UI
│   ├── config.py              ← Settings
│   └── requirements.txt        ← Dependencies
│
├── Setup & Launch
│   ├── setup.sh               ← Auto setup
│   ├── quick_start.py         ← Quick launcher
│   └── .env.example           ← Config template
│
├── Tools
│   └── tools/
│       ├── build_dataset.py   ← Web scraper
│       ├── embeddings.py      ← RAG pipeline
│       ├── agent.py           ← LLM agent
│       └── upload_to_hf.py    ← Cloud upload
│
├── Documentation
│   ├── README.md              ← Main guide
│   ├── GETTING_STARTED.md     ← Setup guide
│   ├── TROUBLESHOOTING.md     ← Debug guide
│   ├── IMPLEMENTATION_SUMMARY.md ← Overview
│   ├── PROJECT_CHECKLIST.md   ← Feature list
│   └── FILES.md               ← This file
│
├── Configuration
│   ├── .env.example           ← Template
│   ├── .gitignore             ← Git settings
│   └── .env                   ← Your config (create)
│
├── Data (created at runtime)
│   └── data/
│       ├── sap_dataset.json
│       ├── rag_index.faiss
│       └── rag_metadata.pkl
│
└── Environment (created at runtime)
    ├── .venv/
    ├── .streamlit/cache/
    └── __pycache__/
```

---

## File Dependencies

### Runtime Dependencies
```
app.py
├── imports: config, embeddings, agent
├── requires: streamlit
└── loads: .env settings

embeddings.py
├── imports: transformers, faiss
├── reads: data/sap_dataset.json
└── outputs: data/rag_index.faiss

agent.py
├── imports: ollama, replicate, huggingface
└── interacts with: LLM providers

build_dataset.py
├── imports: requests, beautifulsoup4
└── outputs: data/sap_dataset.json
```

### Development Dependencies
```
setup.sh
├── creates: .venv
├── installs: requirements.txt
└── generates: .env

quick_start.py
├── calls: build_dataset.py (if needed)
├── calls: embeddings.py (if needed)
└── launches: app.py
```

---

## Key File Purposes

| File | Purpose | Size | Importance |
|------|---------|------|-----------|
| app.py | Main UI | 13KB | Critical |
| build_dataset.py | Data collection | 8.7KB | Core |
| embeddings.py | Vector search | 7.1KB | Core |
| agent.py | LLM integration | 8.7KB | Core |
| config.py | Configuration | 5KB | Important |
| setup.sh | Setup automation | 1.2KB | Helpful |
| README.md | Documentation | 7KB | Important |
| GETTING_STARTED.md | Quick start | 5.3KB | Important |
| TROUBLESHOOTING.md | Debug guide | 10.6KB | Helpful |
| requirements.txt | Dependencies | 664B | Critical |

---

## Modification Guide

### Safe to Edit
- `.env` - Your configuration
- `config.py` - Global settings
- `tools/build_dataset.py` - Data sources

### Advanced Editing
- `tools/agent.py` - LLM customization
- `tools/embeddings.py` - RAG tuning
- `app.py` - UI customization

### Don't Edit
- `requirements.txt` - Package list (unless adding packages)
- `.gitignore` - Git configuration

---

## File Statistics

- **Total Files**: 16+
- **Python Files**: 6
- **Documentation Files**: 5
- **Config Files**: 3
- **Script Files**: 2

- **Total LOC (Code)**: ~1500+
- **Total LOC (Docs)**: ~2000+
- **Total Size**: ~120KB

- **Most Complex**: agent.py, build_dataset.py
- **Most Useful**: README.md, GETTING_STARTED.md

---

## How to Use This Reference

1. **Setting up?** → GETTING_STARTED.md
2. **Understanding code?** → This file + README.md
3. **Making changes?** → See "Modification Guide" above
4. **Got errors?** → TROUBLESHOOTING.md
5. **Need overview?** → IMPLEMENTATION_SUMMARY.md

---

**Last Updated**: 2025-12-09
**Project Status**: Complete & Production Ready ✅
