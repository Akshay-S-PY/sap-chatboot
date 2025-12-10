# config.py
"""
Configuration for SAP Chatbot
Auto-detects HuggingFace Spaces and Streamlit Cloud environments
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============== Environment Detection ==============
# Detect if running in HuggingFace Spaces or Streamlit Cloud
RUNNING_IN_HF_SPACES = os.getenv("SPACE_ID") is not None
RUNNING_IN_STREAMLIT_CLOUD = os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"

# ============== LLM Configuration ==============
# Options: "ollama", "replicate", "huggingface"
# Default to HuggingFace when in HF Spaces, otherwise Ollama
default_provider = "huggingface" if RUNNING_IN_HF_SPACES else "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", default_provider)

# Model names by provider
OLLAMA_MODELS = {
    "fast": "neural-chat",      # 3B, very fast
    "balanced": "mistral",       # 7B, good balance
    "quality": "dolphin-mixtral" # 8x7B, best quality
}

REPLICATE_MODELS = {
    "fast": "meta/llama-2-7b-chat",
    "quality": "mistral-community/mistral-7b-instruct-v0.2"
}

HF_MODELS = {
    "fast": "zephyr",  # HuggingFaceH4/zephyr-7b-beta - fast and efficient
    "balanced": "mistral",  # mistralai/Mistral-7B-Instruct-v0.1 - best quality/speed
    "quality": "llama2"  # meta-llama/Llama-2-7b-chat-hf - high quality
}

# Default model
DEFAULT_MODEL = os.getenv("LLM_MODEL", "mistral")

# API Tokens (if using cloud LLMs)
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_DATASET_REPO = os.getenv("HF_DATASET_REPO", "your-username/sap-dataset")

# ============== RAG Configuration ==============
# Embeddings model (HuggingFace)
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")

# Data paths
DATA_DIR = "data"
DATASET_PATH = os.path.join(DATA_DIR, "sap_dataset.json")
INDEX_PATH = os.path.join(DATA_DIR, "rag_index.faiss")
METADATA_PATH = os.path.join(DATA_DIR, "rag_metadata.pkl")

# RAG parameters
RAG_CHUNK_SIZE = 512
RAG_CHUNK_OVERLAP = 100
RAG_TOP_K = 5

# ============== Scraper Configuration ==============
# Web scraping delays (be respectful!)
SCRAPER_DELAY_MIN = 2
SCRAPER_DELAY_MAX = 5

# Max articles per source
MAX_ARTICLES_PER_SOURCE = 50

# ============== Streamlit Configuration ==============
STREAMLIT_PAGE_CONFIG = {
    "page_title": "SAP Chatbot",
    "page_icon": "🧩",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ============== UI Configuration ==============
TITLE = "🧩 SAP Intelligent Assistant"
SUBTITLE = "Free RAG-based SAP Q&A System"
WELCOME_MESSAGE = """
Welcome to the SAP Intelligent Assistant! 👋

This is a free, open-source RAG (Retrieval-Augmented Generation) system that helps you with:
- SAP Basis administration
- SAP ABAP development
- SAP HANA
- SAP Fiori
- SAP Configuration & Security
- And more!

**How it works:**
1. Your question is searched against a knowledge base of SAP documents
2. Relevant documents are retrieved
3. An AI generates an answer based on the retrieved content

**Features:**
- 100% Free & Open Source
- Local LLM support (Ollama)
- Multi-source data (SAP Community, GitHub, blogs)
- Vector similarity search
- Conversation history

**To get started:**
1. Type your SAP question in the chat box
2. View the sources used for the answer
3. Continue the conversation naturally
"""

# ============== Help Messages ==============
HELP_MESSAGES = {
    "setup_ollama": """
### Setting up Ollama (Local LLM)

1. **Install Ollama**: Download from https://ollama.ai
2. **Start Ollama**: `ollama serve`
3. **Pull a model**: `ollama pull mistral` or `ollama pull neural-chat`
4. **In your terminal**: The server runs on localhost:11434

Supported models:
- **Neural Chat** (3B): Fast, good for quick responses
- **Mistral** (7B): Balanced quality and speed
- **Dolphin Mixtral** (8x7B): Best quality but slower
    """,
    
    "setup_replicate": """
### Setting up Replicate

1. **Get API Token**: https://replicate.com (sign up for free tier)
2. **Set environment variable**: 
   ```bash
   export REPLICATE_API_TOKEN="your_token_here"
   ```
3. **Models available**:
   - Llama 2 7B Chat
   - Mistral 7B
   - And more...
    """,
    
    "setup_huggingface": """
### Setting up HuggingFace

1. **Get API Token**: https://huggingface.co/settings/tokens
2. **Set environment variable**: 
   ```bash
   export HF_API_TOKEN="your_token_here"
   ```
3. **Models available**: Any HuggingFace text-generation model
    """
}

# ============== System Prompts ==============
SYSTEM_PROMPTS = {
    "sap_expert": """You are an expert SAP consultant with deep knowledge of:
- SAP Basis & System Administration
- SAP ABAP & Web Dynpro
- SAP HANA & Database
- SAP Security & Authorization
- SAP Fiori & UI Technologies
- SAP Transport & Change Management
- SAP Performance & Optimization

Provide clear, accurate, practical advice. When citing sources, be specific.
If unsure, acknowledge and suggest official SAP documentation.""",

    "basis_expert": """You are a SAP Basis expert specializing in:
- System administration and monitoring
- Transport management systems
- Background job management
- System performance tuning
- Patch and upgrade management
- System security and authorization

Provide step-by-step guidance with transaction codes and best practices.""",

    "developer": """You are a SAP ABAP developer expert. Help with:
- ABAP programming and development
- Web Dynpro and UI5/Fiori
- Reports and forms
- Interfaces and integration
- Debugging and troubleshooting

Include code examples and best practices."""
}

if __name__ == "__main__":
    print("SAP Chatbot Configuration")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Embeddings Model: {EMBEDDINGS_MODEL}")
