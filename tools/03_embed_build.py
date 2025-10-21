import json, numpy as np, faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

meta = json.loads(Path("index/meta.json").read_text(encoding="utf-8"))
texts = [c["text"] for c in meta]
model_name = "sentence-transformers/all-MiniLM-L6-v2"

print("encoding with", model_name, "…")
model = SentenceTransformer(model_name)
X = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")

dim = X.shape[1]
index = faiss.IndexFlatIP(dim)   # cosine via normalized vectors
index.add(X)

faiss.write_index(index, "index/index.faiss")
Path("index/dim.json").write_text(json.dumps({"dim": int(dim), "model": model_name}), encoding="utf-8")
print("saved index:", X.shape)
