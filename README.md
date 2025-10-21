# SAP Basis Chatbot (Free RAG)

A Streamlit app that answers beginner SAP Basis questions using short, cited passages from public SAP Community blogs (and a few official overviews). No paid APIs or servers.

## Live App
- Deploy on Streamlit Community Cloud: point to `app.py`

## How it works
- **GitHub Actions** (daily or on demand) discovers Basis blog links, fetches rendered pages, extracts text, chunks, embeds (MiniLM), builds a FAISS index.
- **Artifacts** are stored in the repo (if small) or on **Hugging Face Hub** (if large).
- The **Streamlit app** loads the latest index (HF first if configured), retrieves top-k passages and shows a concise answer with citations.

## Run (Streamlit Cloud)
- No setup—Cloud installs `requirements.txt` and runs `app.py`.
- Optional secret: `HF_DATASET_REPO = yourname/sap-basis-rag` (if artifacts live on HF).

## Manual run (optional)
```bash
# Not required if you only use CI + Streamlit Cloud
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export HF_DATASET_REPO=yourname/sap-basis-rag  # if using HF
streamlit run app.py
