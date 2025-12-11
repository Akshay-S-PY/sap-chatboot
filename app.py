# app.py
import os
import streamlit as st
from huggingface_hub import InferenceClient
from supabase import create_client
import numpy as np
import json
from typing import List

# -------- CONFIG ----------
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RESULTS_K = int(os.environ.get("RESULTS_K", 5))

# -------- VALIDATE ----------
if not HF_API_TOKEN or not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error("Missing required secrets: HF_API_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY. Add them as Space Secrets.")
    st.stop()

# -------- CLIENTS ----------
client = InferenceClient(token=HF_API_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --------- HELPERS ----------
def compute_embedding(text: str) -> List[float]:
    """
    Call HF Inference API for embeddings. Returns a flat list[float].
    """
    # Use the new feature_extraction method
    result = client.feature_extraction(text, model=EMBEDDING_MODEL)
    
    # Convert to list of floats
    if hasattr(result, 'tolist'):
        # numpy array
        vec = result.tolist()
    elif isinstance(result, list):
        vec = result
    else:
        raise RuntimeError(f"Unexpected embedding result type: {type(result)}")
    
    # Flatten if nested (some models return [[...]])
    if isinstance(vec, list) and len(vec) > 0 and isinstance(vec[0], list):
        vec = vec[0]
    
    return [float(x) for x in vec]

def search_supabase(query_vector: List[float], k: int = RESULTS_K):
    """
    Call the Postgres RPC function `search_documents` created in Supabase.
    """
    # Supabase client expects JSON serializable types
    payload = {"query_embedding": query_vector, "k": k}
    resp = supabase.rpc("search_documents", payload).execute()
    if getattr(resp, "error", None):
        raise RuntimeError(f"Supabase RPC error: {resp.error}")
    return resp.data or []

# --------- UI ----------
st.set_page_config(page_title="SAP Docs Q&A", page_icon="🔎")
st.title("SAP Docs Q&A — demo")

st.markdown(
    "Ask a question about SAP documentation. The system computes embeddings (Hugging Face) "
    "and finds relevant document chunks (Supabase pgvector)."
)

with st.form("query_form"):
    q = st.text_input("Question", max_chars=800, key="q")
    k = st.slider("Results (k)", min_value=1, max_value=20, value=RESULTS_K)
    submitted = st.form_submit_button("Search")

if submitted and q and q.strip():
    q = q.strip()
    with st.spinner("Computing embedding..."):
        try:
            qvec = compute_embedding(q)
        except Exception as e:
            st.error(f"Embedding failed: {e}")
            st.stop()

    with st.spinner("Searching Supabase..."):
        try:
            rows = search_supabase(qvec, k)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    if not rows:
        st.info("No matches found.")
    else:
        st.success(f"Found {len(rows)} chunks")
        # Simple aggregation: show results ordered by similarity
        for r in rows:
            title = r.get("title", "(no title)")
            chunk_id = r.get("chunk_id", -1)
            sim = r.get("similarity", 0.0)
            content = r.get("content", "")
            st.markdown(f"**{title}** — chunk {chunk_id} — similarity {sim:.4f}")
            st.write(content[:2000])
            st.markdown("---")

# Optional: show debug / health
with st.expander("Diagnostics"):
    st.write(f"Embedding model: `{EMBEDDING_MODEL}`")
    st.write(f"Supabase URL: `{SUPABASE_URL}`")
    st.write(f"Results per query: {RESULTS_K}")
