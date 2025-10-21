import json, numpy as np, faiss, sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

META_PATH = Path("index/meta.json")
DIM_PATH  = Path("index/dim.json")
FAISS_OUT = Path("index/index.faiss")

if not META_PATH.exists():
    print("meta.json missing; nothing to embed.")
    # Write an empty index with known dim to keep app happy
    dim = 384  # all-MiniLM-L6-v2
    index = faiss.IndexFlatIP(dim)
    faiss.write_index(index, str(FAISS_OUT))
    DIM_PATH.write_text(json.dumps({"dim": dim, "model": "sentence-transformers/all-MiniLM-L6-v2"}), encoding="utf-8")
    sys.exit(0)

meta = json.loads(META_PATH.read_text(encoding="utf-8"))
texts = [c.get("text","").strip() for c in meta if c.get("text","").strip()]

if len(texts) == 0:
    print("No non-empty texts; writing empty FAISS index.")
    dim = 384  # MiniLM
    index = faiss.IndexFlatIP(dim)
    faiss.write_index(index, str(FAISS_OUT))
    DIM_PATH.write_text(json.dumps({"dim": dim, "model": "sentence-transformers/all-MiniLM-L6-v2"}), encoding="utf-8")
    sys.exit(0)

model_name = "sentence-transformers/all-MiniLM-L6-v2"
print("encoding with", model_name)
model = SentenceTransformer(model_name)
X = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")

dim = X.shape[1]
index = faiss.IndexFlatIP(dim)   # cosine via normalized vectors
index.add(X)

faiss.write_index(index, str(FAISS_OUT))
DIM_PATH.write_text(json.dumps({"dim": int(dim), "model": model_name}), encoding="utf-8")
print("saved index:", X.shape)
