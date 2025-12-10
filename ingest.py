# ingest.py
import os
import glob
import json
from pathlib import Path
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
DOCS_PATH = os.environ.get("DOCS_PATH", "data/docs")  # path in repo for .txt files
JSON_DATASET_PATH = os.environ.get("JSON_DATASET_PATH", "data/sap_dataset.json")

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

def ingest_json_dataset(json_path):
    path = Path(json_path)
    if not path.exists():
        print(f"JSON dataset not found at {json_path}, skipping JSON ingest.")
        return 0
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    total_rows = 0
    for article in tqdm(data, desc="json-articles"):
        content = article.get("content", "")
        if not content:
            continue
        title = article.get("title") or "SAP Article"
        url = article.get("url")
        source = article.get("source", "sap-json")
        chunks = chunk_text(content)
        rows = []
        for ix, chunk in enumerate(chunks):
            emb = model.encode(chunk).tolist()
            rows.append({
                "source": source,
                "url": url,
                "title": title,
                "content": chunk,
                "chunk_id": ix,
                "embedding": emb,
            })
        if rows:
            res = supabase.table("documents").insert(rows).execute()
            if res.error:
                print(f"Insert error for article {title[:60]}: {res.error}")
            else:
                total_rows += len(rows)
    print(f"Inserted {total_rows} chunks from JSON dataset")
    return total_rows

def main():
    total_inserted = 0

    # Prefer JSON dataset if present
    json_rows = ingest_json_dataset(JSON_DATASET_PATH)
    total_inserted += json_rows or 0

    # Also ingest any text files if present
    files = glob.glob(os.path.join(DOCS_PATH, "*.txt"))
    if files:
        print(f"Found {len(files)} txt docs in {DOCS_PATH}")
        for fp in tqdm(files):
            ingest_file(fp)
    else:
        print(f"No txt docs found in {DOCS_PATH}")

    print(f"Ingestion finished. Total chunks inserted: {total_inserted}")

if __name__ == "__main__":
    main()
