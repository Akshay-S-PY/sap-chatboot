# 📋 DEPLOYMENT: Supabase + HuggingFace Spaces

Your SAP Chatbot now uses **production-grade infrastructure**:
- **Vector DB**: Supabase pgvector
- **App Hosting**: HuggingFace Spaces (Docker → Streamlit)
- **Ingestion**: GitHub Actions (automated)
- **LLM**: HuggingFace Inference API

**Total cost: $0-25/month** (Supabase free or $25 pro)

---

## 📖 Step-by-Step Deployment

### Phase 1: Supabase Setup (10 minutes)

#### 1.1 Create Supabase Project
```bash
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (free)
4. Create organization & project
5. Choose region (closest to you)
6. Wait for initialization (~2 min)
```

#### 1.2 Enable pgvector
```sql
-- In Supabase Dashboard → SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 1.3 Create Documents Table
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

-- Create index for faster search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### 1.4 Create Search Function
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

#### 1.5 Get Credentials
```
In Supabase Dashboard → Settings → API

Copy these:
- Project URL              → SUPABASE_URL
- Anon (public) key       → SUPABASE_ANON_KEY (for app)
- Service_role key        → SUPABASE_SERVICE_ROLE_KEY (for Actions only!)
```

⚠️ **IMPORTANT**: Never expose service_role key in HF Spaces!

---

### Phase 2: GitHub Actions Setup (5 minutes)

#### 2.1 Add GitHub Secrets
```
Your repo → Settings → Secrets and variables → Actions

Add these secrets:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
```

#### 2.2 Verify Workflow
```
Your repo → Actions

You should see: "Ingest & Deploy to HF Spaces"
```

#### 2.3 Manual Trigger (Optional)
```
Actions → "Ingest & Deploy to HF Spaces" → Run workflow

This:
1. Runs ingest.py
2. Loads SAP documents
3. Computes embeddings
4. Inserts into Supabase
```

---

### Phase 3: HuggingFace Spaces Setup (10 minutes)

#### 3.1 Create Space
```
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - Name: sap-chatbot
   - License: Apache 2.0
   - Space SDK: Docker (important!)
   - Visibility: Public
4. Click "Create Space"
```

#### 3.2 Link GitHub Repository
```
Space Settings → "Linked Repository"

Select: your-username/sap-chatbot

✓ Space now auto-syncs with GitHub!
```

#### 3.3 Add Secrets
```
Space Settings → Secrets

Add these (all from Supabase API):
- HF_API_TOKEN          (from https://huggingface.co/settings/tokens)
- SUPABASE_URL          (public, safe to expose)
- SUPABASE_ANON_KEY     (public, safe to expose)
- EMBEDDING_MODEL       (optional, default: all-MiniLM-L6-v2)
- RESULTS_K             (optional, default: 5)
```

#### 3.4 Wait for Build
```
Space will:
1. Detect changes from GitHub
2. Build Docker image (~3 min)
3. Start Streamlit app (~1 min)
4. Status: "Running" (green light)
```

#### 3.5 Test the App
```
1. Click "Open in iframe" or visit the Space URL
2. Wait for Streamlit to load
3. Ask: "How do I monitor SAP background jobs?"
4. Should return answer with sources from Supabase!
```

---

## 📊 File Structure

```
sap-chatbot/
├── app.py                    # Streamlit app (uses HF API + Supabase)
├── ingest.py                 # Ingestion script (GitHub Actions)
├── config.py                 # Configuration
├── Dockerfile                # Docker config (HF Spaces)
├── requirements.txt          # Dependencies (supabase, sentence-transformers)
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions workflow
├── tools/
│   ├── agent.py             # LLM interface
│   ├── embeddings.py        # Embedding utilities
│   └── build_dataset.py     # Dataset builder
├── data/
│   └── sap_dataset.json     # Source documents
├── SUPABASE_SETUP.md        # Detailed Supabase guide
├── README.md                # Main README
└── QUICKSTART_HF_SPACES.md  # Local setup (alternative)
```

---

## 🔄 Workflows

### Adding More Documents

```
1. Update data/sap_dataset.json with new documents
   └─ Run: python tools/build_dataset.py

2. Push to GitHub
   └─ git add . && git commit && git push

3. GitHub Actions auto-runs:
   └─ ingest.py computes embeddings
   └─ Inserts into Supabase
   └─ ~2-5 minutes

4. HF Spaces auto-syncs from GitHub
   └─ New documents immediately available
```

### Updating Code

```
1. Make changes to app.py, config.py, etc.
2. Push to GitHub
3. HF Spaces auto-rebuilds and redeploys (~3 min)
4. App is live with new features!
```

### Manual Ingestion (Local)

```bash
# Set env vars
export SUPABASE_URL="https://..."
export SUPABASE_SERVICE_ROLE_KEY="eyJ..."
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Run ingestion
python ingest.py

# Logs show progress:
# - Loading 47 documents
# - Computing embeddings
# - Inserting into Supabase
# - Total chunks: 234
```

---

## 🔐 Security

### Keys & Secrets

| Key | Use | Where | Public? |
|-----|-----|-------|---------|
| HF_API_TOKEN | API access | HF Spaces Secrets | ❌ No |
| SUPABASE_URL | DB connection | HF Spaces Secrets | ✅ Yes |
| SUPABASE_ANON_KEY | Row-level access (RLS) | HF Spaces Secrets | ✅ Yes (limited) |
| SUPABASE_SERVICE_ROLE_KEY | Bypass RLS | GitHub Secrets only | ❌ NO! |

### Row-Level Security (RLS)

Supabase uses RLS policies to control access:
- `SUPABASE_ANON_KEY`: Can read from `documents` table (RLS policy)
- `SUPABASE_SERVICE_ROLE_KEY`: Can bypass RLS (ingestion only)

✅ **Best Practice**: Keep service_role key only in GitHub Actions

---

## 📈 Scaling

### Free Tier Limits
- 500MB database
- 2GB file storage
- Limited API calls
- Great for testing!

### When to Upgrade Supabase

```
Free tier is enough if:
- Documents < 500MB
- Users < 100/month
- Searches < 1000/day

Upgrade to Pro ($25/mo) when:
- Growing beyond limits
- Need higher rate limits
- Want priority support
```

### Cost Optimization

```
Current (Free):
- HF Spaces: $0
- Supabase: $0
- HF Inference API: $0
- GitHub Actions: $0
- Total: $0

With Supabase Pro ($25):
- HF Spaces: $0
- Supabase: $25
- HF Inference API: $0
- GitHub Actions: $0
- Total: $25/month

Supports:
- 100+ concurrent users
- 1TB+ documents
- Unlimited searches
```

---

## ✅ Checklist

### Before Deploying
- [ ] Supabase project created
- [ ] pgvector enabled
- [ ] documents table created
- [ ] search_documents() function created
- [ ] GitHub Actions secrets added
- [ ] HF Space created and linked to GitHub
- [ ] HF Space secrets configured
- [ ] data/sap_dataset.json in repo

### Deployment Day
- [ ] Run GitHub Actions ingestion (manual trigger)
- [ ] Wait for ingestion to complete
- [ ] HF Space auto-syncs and builds
- [ ] App available at Space URL
- [ ] Test with sample query
- [ ] Share URL with team

### Post-Deployment
- [ ] Monitor ingestion logs
- [ ] Monitor app performance
- [ ] Add more documents as needed
- [ ] Gather feedback from users
- [ ] Plan upgrades if needed

---

## 🆘 Troubleshooting

### "Module not found: supabase"
```bash
# Install missing packages
pip install -r requirements.txt
```

### "pgvector not found"
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### "RPC function not found"
```sql
-- Create function in Supabase SQL Editor
CREATE OR REPLACE FUNCTION search_documents...
```

### "Embedding dimension mismatch"
```python
# Check model outputs 384 dimensions
# Table must be VECTOR(384)
```

### "Ingestion too slow"
```python
# In ingest.py, increase batch size
BATCH_SIZE = 200  # default: 100
```

### "App can't connect to Supabase"
- Verify `SUPABASE_URL` in secrets
- Verify `SUPABASE_ANON_KEY` in secrets
- Check RLS policies allow read from documents

### "Search results are empty"
- Verify ingestion completed
- Check documents table has rows
- Test search_documents() directly in Supabase

---

## 🚀 Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure GitHub Actions
3. ✅ Create HF Space with secrets
4. ✅ Trigger ingestion manually
5. ✅ Deploy and test
6. ✅ Share with your SAP team!

---

## 📚 Resources

- **Supabase**: https://supabase.com/docs
- **pgvector**: https://github.com/pgvector/pgvector
- **HF Spaces**: https://huggingface.co/docs/hub/spaces
- **Docker on HF**: https://huggingface.co/docs/hub/spaces-sdks-docker

---

**Your production-grade SAP chatbot is ready! 🎉**
