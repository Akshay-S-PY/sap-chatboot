# app.py
import json, os
from pathlib import Path
import numpy as np
import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download, list_repo_files

st.set_page_config(page_title="SAP Basis Chatbot", page_icon="🧩", layout="wide")
st.title("🧩 SAP Basis Expert Assistant")
st.caption("Free RAG over comprehensive SAP Basis documentation and community content")

# Configuration
HF_REPO = os.getenv("HF_DATASET_REPO", "your-username/sap-basis-rag")  # Set this in Streamlit Cloud
USE_HF = True  # Always use HF for robustness

@st.cache_resource(show_spinner="Loading knowledge base...")
def load_artifacts():
    """Load FAISS index and metadata from Hugging Face Hub"""
    try:
        # Get available files
        files = set(list_repo_files(HF_REPO))
        st.info(f"Available files in {HF_REPO}: {list(files)}")
        
        # Download artifacts
        faiss_path = hf_hub_download(HF_REPO, filename="index.faiss")
        meta_path = hf_hub_download(HF_REPO, filename="meta.json") 
        dim_path = hf_hub_download(HF_REPO, filename="dim.json")
        
        # Load artifacts
        index = faiss.read_index(faiss_path)
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        dim_data = json.loads(Path(dim_path).read_text(encoding="utf-8"))
        dim = dim_data["dim"]
        
        st.success(f"✓ Loaded {len(meta)} knowledge passages")
        return index, meta, dim
        
    except Exception as e:
        st.error(f"Failed to load knowledge base: {e}")
        st.info("Please ensure:")
        st.info("1. HF_DATASET_REPO is set in Streamlit secrets")
        st.info("2. The repository contains index.faiss, meta.json, and dim.json")
        st.info("3. You have access to the repository")
        return None, [], 384

@st.cache_resource(show_spinner=False)
def load_embedder():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_query(model, query):
    return model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

def search(index, query_vector, k=5):
    similarities, indices = index.search(query_vector, k)
    return indices[0].tolist(), similarities[0].tolist()

def format_answer(query, context_passages):
    if not context_passages:
        return "I couldn't find relevant information in my knowledge base. Try rephrasing your question or ask about SAP Basis administration, transport management, system monitoring, or security."
    
    # Build concise answer
    answer_parts = []
    for i, passage in enumerate(context_passages, 1):
        # Extract first meaningful sentences
        text = passage["text"].replace("\n", " ").strip()
        sentences = [s.strip() for s in text.split(". ") if s.strip()]
        if sentences:
            snippet = ". ".join(sentences[:2]) + "."
            answer_parts.append(f"{snippet} [{i}]")
    
    # Format output
    response = []
    response.append("**Answer:**")
    response.append(" ".join(answer_parts) if answer_parts else "Relevant information found in sources below.")
    
    response.append("\n**Sources:**")
    for i, passage in enumerate(context_passages, 1):
        title = passage["title"][:80] + "..." if len(passage["title"]) > 80 else passage["title"]
        response.append(f"[{i}] **{title}** — {passage['url']}")
    
    return "\n\n".join(response)

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index, st.session_state.meta, st.session_state.dim = load_artifacts()
if "embedder" not in st.session_state:
    st.session_state.embedder = load_embedder()

# Sidebar
with st.sidebar:
    st.header("🔧 Settings")
    k = st.slider("Number of sources", 3, 10, 5)
    
    st.header("💡 Sample Questions")
    sample_questions = [
        "How do I analyze work processes using SM50/SM66?",
        "What is TMS and how do I set up transport routes?",
        "How to read system logs in SM21?",
        "What are kernel patches and how to apply them?",
        "How to monitor system performance?",
        "What is client administration in SAP?",
        "How to manage users and authorizations?",
        "What is background job processing?"
    ]
    
    for q in sample_questions:
        if st.button(f"• {q}", key=f"btn_{hash(q)}"):
            st.session_state.query = q

# Main interface
st.markdown("""
Ask me about:
- **System Administration** (client copy, user management)
- **Transport Management** (TMS, STMS, transport routes)  
- **Performance Monitoring** (work processes, system logs)
- **Security & Authorization** (profiles, roles)
- **Database Administration** (backup, recovery)
- **Kernel & Patches** (SPAM, SAINT)
""")

# Query input
query = st.text_input(
    "Ask your SAP Basis question:",
    value=st.session_state.get("query", ""),
    placeholder="e.g., How do I troubleshoot work processes?"
)

if st.button("Search", type="primary") or query:
    if not query.strip():
        st.warning("Please enter a question")
    elif st.session_state.index is None:
        st.error("Knowledge base not loaded. Please check configuration.")
    else:
        with st.spinner("Searching knowledge base..."):
            try:
                # Search
                query_vector = embed_query(st.session_state.embedder, query)
                indices, similarities = search(st.session_state.index, query_vector, k)
                
                # Get results
                results = [st.session_state.meta[i] for i in indices if 0 <= i < len(st.session_state.meta)]
                
                # Display results
                if results:
                    st.markdown(format_answer(query, results))
                    
                    # Show detailed passages
                    with st.expander("📖 View Detailed Passages"):
                        for i, passage in enumerate(results, 1):
                            st.markdown(f"**[{i}] {passage['title']}**")
                            st.markdown(f"*Source: {passage['url']}*")
                            st.write(passage["text"])
                            st.markdown("---")
                else:
                    st.info("No relevant information found. Try rephrasing your question.")
                    
            except Exception as e:
                st.error(f"Search error: {e}")

# Footer
st.markdown("---")
st.caption("""
**Note**: This assistant uses publicly available SAP documentation and community content. 
Always verify critical information with official SAP resources and documentation.
""")
