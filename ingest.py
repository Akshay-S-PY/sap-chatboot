# ingest.py
import os
import glob
from supabase import create_client
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

# load local .env for manual runs (GH Actions will use secrets)
load_dotenv()

# config from env
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
DOCS_PATH = os.environ.get("DOCS_PATH", "data/docs")  # path in repo

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise SystemExit(
        "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in env (local .env or GitHub Secrets) before running."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
model = SentenceTransformer(EMBEDDING_MODEL)

def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        # move with overlap
        start = end - overlap if end - overlap > start else end
    return chunks

def ingest_file(filepath, source="sap-docs-scrape"):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    title = os.path.basename(filepath)
    chunks = chunk_text(text)
    rows = []
    for ix, chunk in enumerate(chunks):
        emb = model.encode(chunk).tolist()
        row = {
            "source": source,
            "url": None,
            "title": title,
            "content": chunk,
            "chunk_id": ix,
            "embedding": emb
        }
        rows.append(row)
    if rows:
        res = supabase.table("documents").insert(rows).execute()
        if res.error:
            print(f"Insert error for {filepath}: {res.error}")
        else:
            print(f"Inserted {len(rows)} chunks for {filepath}")
    return

def main():
    files = glob.glob(os.path.join(DOCS_PATH, "*.txt"))
    print(f"Found {len(files)} docs in {DOCS_PATH}")
    for fp in tqdm(files):
        ingest_file(fp)
    print("Ingestion finished.")

if __name__ == "__main__":
    main()
