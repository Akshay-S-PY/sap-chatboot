# 🗄️ Supabase Vector Database Setup

Your SAP Chatbot now uses **Supabase + pgvector** for production-grade vector search!

## Architecture

```
GitHub Actions (Ingestion)
    ↓ (SUPABASE_SERVICE_ROLE_KEY)
  ingest.py
    ├─ Load SAP documents
    ├─ Compute embeddings (sentence-transformers)
    └─ Insert into Supabase (pgvector)
           ↓
    HuggingFace Spaces (Streamlit App)
         ├─ User asks question
         ├─ HF Inference API computes embedding
         ├─ Supabase RPC search_documents()
         ├─ Retrieve top-k results
         └─ Generate answer with HF Inference API
```

## Quick Setup

### 1. Create Supabase Project

1. Go to https://supabase.com
2. Sign up (free tier available)
3. Create new project
4. Wait for database initialization (~2 min)

### 2. Enable pgvector

```sql
-- In Supabase SQL Editor:
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Create Documents Table

```sql
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  source TEXT,
  url TEXT,
  title TEXT,
  content TEXT,
  chunk_id INT,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 4. Create Search Function

```sql
CREATE OR REPLACE FUNCTION search_documents(query_embedding VECTOR, k INT DEFAULT 5)
RETURNS TABLE(id BIGINT, source TEXT, url TEXT, title TEXT, content TEXT, chunk_id INT, distance FLOAT8) AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.source,
    documents.url,
    documents.title,
    documents.content,
    documents.chunk_id,
    1 - (documents.embedding <=> query_embedding) AS distance
  FROM documents
  ORDER BY documents.embedding <=> query_embedding
  LIMIT k;
END;
$$ LANGUAGE plpgsql;
```

### 5. Get Credentials

In Supabase dashboard:
1. Go to **Settings → API**
2. Copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY` (for Streamlit app)
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (for GitHub Actions only!)

⚠️ **NEVER put service_role key in Space Secrets!** Only in GitHub Actions.

### 6. Run Local Ingestion (Optional)

```bash
# Set env vars locally
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Run ingestion
python ingest.py
```

### 7. Configure GitHub Actions Secrets

In your GitHub repo:
1. Settings → Secrets and variables → Actions
2. Add new secrets:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_SERVICE_ROLE_KEY` = service role key (for ingestion)

### 8. Configure HF Space Secrets

In HuggingFace Space Settings → Secrets:
- `HF_API_TOKEN` = your HF token
- `SUPABASE_URL` = your Supabase URL
- `SUPABASE_ANON_KEY` = anon public key (safe to expose)
- `EMBEDDING_MODEL` = (optional) embedding model ID
- `RESULTS_K` = (optional) number of results (default: 5)

---

## File Structure

```
sap-chatbot/
├── app.py                    # Streamlit UI (uses HF API + Supabase RPC)
├── ingest.py                 # Ingestion script (uses sentence-transformers)
├── Dockerfile                # Docker config for HF Spaces
├── requirements.txt          # Python dependencies (includes supabase, sentence-transformers)
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions: ingest + deploy
└── data/
    └── sap_dataset.json      # Source documents
```

---

## Deployment Flow

### First Deployment

1. **GitHub**: Push code to `main` branch
2. **GitHub Actions**: 
   - Runs `ingest.py` with `SUPABASE_SERVICE_ROLE_KEY`
   - Ingests documents into Supabase
   - Workflow completes
3. **HF Spaces**:
   - Auto-syncs from GitHub (Linked Repository)
   - Launches Streamlit app
   - App connects to Supabase with `SUPABASE_ANON_KEY`

### Update Knowledge Base

To add more SAP documents:

1. Update `data/sap_dataset.json` with new documents
2. Push to GitHub
3. GitHub Actions auto-runs ingestion
4. New documents available in Supabase
5. HF Spaces app immediately sees new data

---

## API Endpoints

### Streamlit App (HF Spaces)

- Uses HF Inference API for embeddings
- Calls Supabase RPC `search_documents(query_embedding, k)`
- Generates answers with HF Inference API

### ingest.py (GitHub Actions)

- Uses local `sentence-transformers` for embeddings
- Inserts directly to Supabase with service role key
- Runs on schedule or manual trigger

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Compute embedding | 50-100ms | Local sentence-transformers |
| Vector search | 10-50ms | pgvector with IVFFlat index |
| HF Inference (answer) | 10-30s | Cloud API |
| Total response | 10-30s | Dominated by LLM generation |

---

## Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| Supabase (free tier) | FREE | 500MB DB + 2GB file storage |
| Supabase (paid) | $25+/mo | More storage, more API calls |
| HF Inference API | FREE | Rate limited, generous |
| GitHub Actions | FREE | 2000 min/month |
| HF Spaces | FREE | 5+ concurrent users |
| **TOTAL** | **$0-25/mo** | Scales with usage |

**Upgrade to paid Supabase when:**
- Dataset grows beyond 500MB
- Vector searches become slow
- Need higher API rate limits

---

## Troubleshooting

### "pgvector not found"
- Enable pgvector extension in Supabase SQL Editor
- Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### "RPC function not found"
- Copy search_documents SQL function into Supabase
- Run in SQL Editor
- Wait for function to compile

### "Embedding dimension mismatch"
- Model uses 384 dims: `sentence-transformers/all-MiniLM-L6-v2`
- If changing model, recreate VECTOR(new_dim) in table

### "Ingestion too slow"
- Increase BATCH_SIZE in ingest.py
- Run on larger GitHub Actions runner
- Consider async ingestion

### "Search results irrelevant"
- Check embedding model matches
- Verify documents chunked correctly
- Try different chunk_size/overlap in ingest.py

---

## Advanced: Custom Embeddings

To use different embedding model:

### Local (ingest.py)
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # 768 dims
```

### Recreate table with new dimensions
```sql
ALTER TABLE documents ALTER COLUMN embedding TYPE vector(768);
```

### Update app.py
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

---

## Next Steps

1. ✅ Create Supabase project
2. ✅ Enable pgvector and create table
3. ✅ Add GitHub Actions secrets
4. ✅ Push code (triggers ingestion)
5. ✅ Configure HF Space secrets
6. ✅ Test: "How do I monitor SAP jobs?"
7. ✅ Share with team!

---

## Resources

- 📚 [Supabase Docs](https://supabase.com/docs)
- 📦 [pgvector Docs](https://github.com/pgvector/pgvector)
- 🤗 [HF Inference API](https://huggingface.co/docs/api-inference)
- 🔐 [Supabase Security Best Practices](https://supabase.com/docs/guides/api-keys)

---

**Your production-grade SAP chatbot is ready! 🚀**
