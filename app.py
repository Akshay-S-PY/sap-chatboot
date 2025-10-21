import json, os
from pathlib import Path
import numpy as np
import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer
from huggingface_hub import hf_hub_download, list_repo_files

st.set_page_config(page_title="SAP Basis Chatbot", page_icon="🧩", layout="wide")
st.title("🧩 SAP Basis Chatbot")
st.caption("Free RAG over beginner-friendly SAP Basis posts. Unofficial; verify via SAP Help Portal.")

HF_REPO = os.getenv("HF_DATASET_REPO")  # e.g. "yourname/sap-basis-rag"
USE_HF = bool(HF_REPO)

@st.cache_resource(show_spinner=True)
def load_artifacts():
    if USE_HF:
        files = set(list_repo_files(HF_REPO))
        def pick(*names):
            for n in names:
                if n in files: return n
            raise FileNotFoundError(names)
        faiss_file = pick("index.faiss","index/index.faiss")
        meta_file  = pick("meta.json","index/meta.json")
        dim_file   = pick("dim.json","index/dim.json")
        faiss_path = hf_hub_download(HF_REPO, filename=faiss_file)
        meta_path  = hf_hub_download(HF_REPO, filename=meta_file)
        dim_path   = hf_hub_download(HF_REPO, filename=dim_file)
    else:
        faiss_path = "index/index.faiss"
        meta_path  = "index/meta.json"
        dim_path   = "index/dim.json"

    index = faiss.read_index(faiss_path)
    meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
    dim  = json.loads(Path(dim_path).read_text(encoding="utf-8"))["dim"]
    return index, meta, dim

@st.cache_resource(show_spinner=False)
def load_embedder(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)

def embed_query(model, q: str) -> np.ndarray:
    return model.encode([q], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

def search(index, qvec, k=5):
    sims, ids = index.search(qvec, k)
    return ids[0].tolist(), sims[0].tolist()

def compose_answer(query, ctx):
    lines = ["**Answer (concise):**"]
    bits = []
    for i, item in enumerate(ctx, 1):
        text = item["text"].replace("\n", " ").strip()
        sents = [s.strip() for s in text.split(". ") if s.strip()]
        snippet = ". ".join(sents[:2])
        if snippet:
            bits.append(f"{snippet}. [{i}]")
    lines.append(" ".join(bits) if bits else "I couldn’t find a relevant passage.")
    lines.append("\n**Sources:**")
    for i, item in enumerate(ctx, 1):
        lines.append(f"[{i}] **{item['title']}** — {item['url']}")
    return "\n\n".join(lines)

with st.sidebar:
    st.header("Settings")
    k = st.slider("Top-K passages", 3, 10, 5)
    default_domains = "community.sap.com, help.sap.com"
    domain_filter = st.text_input("Only include domains (comma-sep)", value=default_domains)
    show_passages = st.checkbox("Show retrieved passages", value=False)
    st.markdown("---")
    try:
        index, meta, dim = load_artifacts()
        embedder = load_embedder()
        st.success(f"Index loaded • {len(meta)} passages • dim {dim}")
    except Exception as e:
        st.error("Failed to load artifacts. Ensure index files exist or set HF_DATASET_REPO secret.")
        st.exception(e)

st.markdown("Try:\n\n```\nHow do I analyze work processes (SM50/SM66)?\nWhat is TMS and how do I set up transport routes?\nHow to read system logs (SM21)?\nWhat are kernel patches and how to apply?\n```")
q = st.text_input("Ask a SAP Basis question")
go = st.button("Search")

if go and q.strip():
    with st.spinner("Retrieving…"):
        qvec = embed_query(embedder, q)
        ids, sims = search(index, qvec, k=max(k,1))
        rows = [meta[i] for i in ids if 0 <= i < len(meta)]
        if domain_filter.strip():
            allowed = {d.strip().lower() for d in domain_filter.split(",") if d.strip()}
            filt = [r for r in rows if any(d in r["url"].lower() for d in allowed)]
            rows = filt or rows
        st.markdown(compose_answer(q, rows[:k]))
        if show_passages and rows:
            st.markdown("---")
            st.subheader("Retrieved passages")
            for i, r in enumerate(rows[:k], 1):
                with st.expander(f"[{i}] {r['title']} — {r['url']}"):
                    st.write(r["text"])
