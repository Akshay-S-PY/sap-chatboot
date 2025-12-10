# tools/embeddings.py
"""
Vector Store & RAG Pipeline using Free Tools
- Sentence Transformers (MiniLM - fast, 33M params)
- FAISS (CPU-based vector search)
- HuggingFace Hub integration for cloud deployment
- No API costs for embeddings
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import time
import os

# Optional HuggingFace Hub support
try:
    from huggingface_hub import hf_hub_download, HfApi
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False

class RAGPipeline:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize RAG with local embeddings
        
        Args:
            model_name: HuggingFace model for embeddings
                - all-MiniLM-L6-v2: Small, fast, 33M params
                - all-mpnet-base-v2: Larger, better quality, 110M params
        """
        print(f"Loading embeddings model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.documents = []
        self.index = None
        self.metadata = []
    
    def create_chunks(self, text, chunk_size=512, overlap=100):
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > 50:  # Skip tiny chunks
                chunks.append(chunk)
        
        return chunks
    
    def build_index(self, dataset_path="data/sap_dataset.json"):
        """Build FAISS index from dataset"""
        print(f"Loading dataset from {dataset_path}...")
        
        if not Path(dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        print(f"Processing {len(dataset)} documents...")
        
        all_embeddings = []
        chunk_id = 0
        
        for doc_idx, doc in enumerate(dataset):
            title = doc.get('title', 'Unknown')
            content = doc.get('content', '')
            url = doc.get('url', '')
            source = doc.get('source', 'unknown')
            
            # Create chunks
            chunks = self.create_chunks(content)
            
            for chunk in chunks:
                # Create combined text for better search
                text = f"{title}. {chunk}"
                
                self.metadata.append({
                    'chunk_id': chunk_id,
                    'doc_idx': doc_idx,
                    'title': title,
                    'url': url,
                    'source': source,
                    'chunk': chunk[:200],  # Preview
                    'full_text': text
                })
                
                chunk_id += 1
            
            print(f"  [{doc_idx + 1}/{len(dataset)}] {title[:50]}: {len(chunks)} chunks")
        
        if not self.metadata:
            raise ValueError("No documents to index!")
        
        # Generate embeddings
        print(f"\nGenerating embeddings for {len(self.metadata)} chunks...")
        texts = [m['full_text'] for m in self.metadata]
        
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Build FAISS index
        print("Building FAISS index...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings.astype(np.float32))
        
        print(f"✅ Index built with {self.index.ntotal} vectors")
        return self.index
    
    def search(self, query, top_k=5):
        """Search for similar documents"""
        if self.index is None:
            raise ValueError("Index not built! Call build_index() first.")
        
        # Embed query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    'score': float(1 / (1 + distance)),  # Convert distance to similarity
                    'distance': float(distance),
                    'title': meta['title'],
                    'url': meta['url'],
                    'source': meta['source'],
                    'chunk': meta['chunk'],
                    'full_text': meta['full_text'][:500]
                })
        
        return results
    
    def save(self, index_path="data/rag_index.faiss", meta_path="data/rag_metadata.pkl"):
        """Save index and metadata"""
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        
        if self.index:
            faiss.write_index(self.index, index_path)
            print(f"✅ Index saved to {index_path}")
        
        with open(meta_path, 'wb') as f:
            pickle.dump(self.metadata, f)
            print(f"✅ Metadata saved to {meta_path}")
    
    def load(self, index_path="data/rag_index.faiss", meta_path="data/rag_metadata.pkl"):
        """Load index and metadata"""
        if Path(index_path).exists():
            self.index = faiss.read_index(index_path)
            print(f"✅ Index loaded from {index_path}")
        
        if Path(meta_path).exists():
            with open(meta_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✅ Metadata loaded from {meta_path}")
    
    def load_from_hf_hub(self, repo_id: str, index_filename="rag_index.faiss", meta_filename="rag_metadata.pkl"):
        """Load index and metadata from HuggingFace Hub (for HF Spaces)"""
        if not HAS_HF_HUB:
            raise ImportError("huggingface_hub required. Install with: pip install huggingface-hub")
        
        try:
            print(f"Loading from HF Hub: {repo_id}")
            
            # Download index file
            print(f"Downloading {index_filename}...")
            index_path = hf_hub_download(
                repo_id=repo_id,
                filename=index_filename,
                repo_type="dataset"
            )
            self.index = faiss.read_index(index_path)
            print(f"✅ Index loaded from {repo_id}")
            
            # Download metadata file
            print(f"Downloading {meta_filename}...")
            meta_path = hf_hub_download(
                repo_id=repo_id,
                filename=meta_filename,
                repo_type="dataset"
            )
            with open(meta_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✅ Metadata loaded from {repo_id}")
            
        except Exception as e:
            print(f"❌ Failed to load from HF Hub: {e}")
            raise
    
    def get_context(self, query, top_k=5):
        """Get context for LLM prompt"""
        results = self.search(query, top_k=top_k)
        
        context = "SAP Knowledge Base:\n\n"
        for i, result in enumerate(results, 1):
            context += f"[Source {i}] {result['title']}\n"
            context += f"URL: {result['url']}\n"
            context += f"Content: {result['full_text']}\n\n"
        
        return context


# Standalone functions for easy use
def build_rag_index():
    """Build RAG index from dataset"""
    rag = RAGPipeline()
    rag.build_index()
    rag.save()
    return rag


def load_rag_index():
    """Load existing RAG index"""
    rag = RAGPipeline()
    rag.load()
    return rag


if __name__ == "__main__":
    # Build index
    print("Building RAG index...")
    rag = build_rag_index()
    
    # Test search
    test_queries = [
        "How to monitor SAP background jobs?",
        "SAP transport management system setup",
        "SAP performance tuning tips",
    ]
    
    print("\n" + "="*60)
    print("Testing RAG Search")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Title: {result['title']}")
            print(f"    Score: {result['score']:.3f}")
            print(f"    Source: {result['source']}")
            print(f"    Preview: {result['chunk'][:100]}...")
