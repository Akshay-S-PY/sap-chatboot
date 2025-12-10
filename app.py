import os
import streamlit as st
from huggingface_hub import InferenceApi
from supabase import create_client
import numpy as np

# ---- Config (read from env / Space secrets) ----
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RESULTS_K = int(os.environ.get("RESULTS_K", 5))

if not HF_API_TOKEN or not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error("Missing one of HF_API_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY. Add them as Space Secrets.")
    st.stop()

# ---- Clients ----
inference = InferenceApi(repo_id=EMBEDDING_MODEL, token=HF_API_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.title("SAP Docs Q&A — demo")

q = st.text_input("Ask a question about SAP docs:", "")

if st.button("Search") and q.strip():
    with st.spinner("Computing embeddings..."):
        # Hugging Face InferenceApi for embeddings returns list[float]
        emb_res = inference(inputs=q)  # for sentence transformers, this returns embedding vector
        # Some models return nested lists; flatten robustly:
        if isinstance(emb_res, dict) and "error" in emb_res:
            st.error(f"Hugging Face error: {emb_res['error']}")
            st.stop()
        # Try to coerce into 1D float list
        if isinstance(emb_res, list) and len(emb_res) > 0 and isinstance(emb_res[0], list):
            query_vector = emb_res[0]
        else:
            query_vector = emb_res

    # Convert to Python list of floats (Postgres expects array-like)
    query_vector = [float(x) for x in query_vector]

    with st.spinner("Querying Supabase..."):
        # Call the search_documents RPC we created server-side
        # supabase.rpc expects the parameter names to match function signature
        # We pass query_embedding as a list (Postgres 'vector' accepts array-like)
        try:
            # Note: the python supabase client will convert the list to a JSON payload
            rpc_resp = supabase.rpc("search_documents", {"query_embedding": query_vector, "k": RESULTS_K}).execute()
        except Exception as e:
            st.error(f"Error calling Supabase RPC: {e}")
            st.stop()

        if rpc_resp.error:
            st.error(f"Supabase error: {rpc_resp.error.message if hasattr(rpc_resp.error, 'message') else rpc_resp.error}")
            st.stop()

        rows = rpc_resp.data or []
        if not rows:
            st.info("No results found.")
        else:
            st.success(f"Found {len(rows)} results")
            for r in rows:
                st.markdown(f"**{r.get('title','(no title)')}** — chunk {r.get('chunk_id')}, similarity: {r.get('similarity'):.4f}")
                st.write(r.get("content", "")[:1000])  # show first 1k chars
                st.markdown("---")
