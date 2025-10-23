# app.py
import streamlit as st
import json
from huggingface_hub import hf_hub_download
import os
import re

st.set_page_config(
    page_title="SAP Basis Chatbot",
    page_icon="🧩",
    layout="wide"
)

st.title("🧩 SAP Basis Assistant")
st.markdown("Ask questions about SAP Basis administration, monitoring, and best practices.")

# Configuration - using your GitHub secrets
HF_REPO = os.getenv("HF_DATASET_REPO", "your-username/sap-basis-dataset")  # Will be set in Streamlit Cloud

@st.cache_resource
def load_dataset():
    """Load dataset from Hugging Face"""
    try:
        st.info("📥 Loading SAP Basis knowledge base...")
        dataset_path = hf_hub_download(
            repo_id=HF_REPO,
            filename="sap_basis_dataset.json",
            token=os.getenv("HF_TOKEN")  # Optional: if dataset is private
        )
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        st.success(f"✅ Loaded {len(data)} SAP Basis documents")
        return data
        
    except Exception as e:
        st.error(f"❌ Failed to load dataset: {e}")
        st.info("Please make sure:")
        st.info("1. HF_DATASET_REPO is set in Streamlit secrets")
        st.info("2. The dataset exists at the specified repository")
        return []

def search_documents(query, documents, top_k=5):
    """Simple but effective search"""
    query = query.lower().strip()
    results = []
    
    for doc in documents:
        score = 0
        
        # Combine title and content for search
        text = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
        
        # Exact phrase matches
        if query in text:
            score += 20
            
        # Individual word matches
        query_words = query.split()
        matches = sum(1 for word in query_words if word in text)
        score += matches * 2
        
        # Title matches are more important
        title = doc.get('title', '').lower()
        if any(word in title for word in query_words):
            score += 10
            
        if score > 0:
            results.append((score, doc))
    
    # Sort by relevance
    results.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in results[:top_k]]

def format_answer(results, query):
    """Format the search results into a nice answer"""
    if not results:
        return "I couldn't find specific information about that topic in my knowledge base. Try asking about:\n\n- SAP Basis administration\n- System monitoring (SM50, SM66)\n- Transport Management (TMS)\n- User and security management\n- Background job processing"
    
    response = []
    response.append("## 📚 Found Information\n")
    
    for i, doc in enumerate(results, 1):
        title = doc.get('title', 'SAP Basis Article')
        content = doc.get('content', '')
        
        # Extract relevant snippet
        sentences = re.split(r'[.!?]+', content)
        snippet = '. '.join(sentences[:3]) + '.' if sentences else content[:300] + "..."
        
        response.append(f"**{i}. {title}**")
        response.append(f"{snippet}")
        response.append(f"*Source: {doc.get('url', 'SAP Community')}*")
        response.append("---")
    
    return "\n\n".join(response)

# Load dataset
dataset = load_dataset()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Number of results", 3, 10, 5)
    
    st.header("💡 Sample Questions")
    samples = [
        "How to monitor work processes?",
        "What is TMS in SAP?",
        "How to check system logs?",
        "User administration best practices",
        "Background job monitoring"
    ]
    
    for sample in samples:
        if st.button(sample, use_container_width=True):
            st.session_state.query = sample

# Main interface
if dataset:
    query = st.text_input(
        "💬 Ask your SAP Basis question:",
        placeholder="e.g., How do I analyze work processes using SM50?",
        value=st.session_state.get('query', '')
    )
    
    if st.button("🔍 Search", type="primary") or query:
        if query.strip():
            with st.spinner("Searching knowledge base..."):
                results = search_documents(query, dataset, top_k)
                st.markdown(format_answer(results, query))
else:
    st.error("No dataset available. Please check the configuration.")

# Footer
st.markdown("---")
st.caption("💡 This assistant uses publicly available SAP Community content. Always verify critical information with official SAP documentation.")
