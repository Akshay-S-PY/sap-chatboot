# app.py
import os
import streamlit as st
from huggingface_hub import InferenceClient
from supabase import create_client
from typing import List

# -------- CONFIG ----------
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.environ.get("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
RESULTS_K = int(os.environ.get("RESULTS_K", 5))

# -------- VALIDATE ----------
if not HF_API_TOKEN or not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error("Missing required secrets: HF_API_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY. Add them as Space Secrets.")
    st.stop()

# -------- CLIENTS ----------
client = InferenceClient(token=HF_API_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# -------- SYSTEM PROMPT ----------
SYSTEM_PROMPT = """You are an SAP documentation assistant. Your job is to answer questions based ONLY on the provided context documents.

STRICT RULES:
1. ONLY use information from the provided context to answer
2. If the context doesn't contain enough information to answer, say "I don't have enough information in my knowledge base to answer this question."
3. DO NOT use any prior knowledge - only the provided documents
4. Always be helpful and format your answers clearly
5. If relevant, mention which source document the information came from

Remember: You are grounded to the provided context only. Do not make up information."""

# --------- HELPERS ----------
def compute_embedding(text: str) -> List[float]:
    """
    Call HF Inference API for embeddings. Returns a flat list[float].
    """
    result = client.feature_extraction(text, model=EMBEDDING_MODEL)
    
    # Convert to list of floats
    if hasattr(result, 'tolist'):
        vec = result.tolist()
    elif isinstance(result, list):
        vec = result
    else:
        raise RuntimeError(f"Unexpected embedding result type: {type(result)}")
    
    # Flatten if nested
    if isinstance(vec, list) and len(vec) > 0 and isinstance(vec[0], list):
        vec = vec[0]
    
    return [float(x) for x in vec]


def search_supabase(query_vector: List[float], k: int = RESULTS_K):
    """
    Call the Postgres RPC function `search_documents` created in Supabase.
    """
    payload = {"query_embedding": query_vector, "k": k}
    resp = supabase.rpc("search_documents", payload).execute()
    if getattr(resp, "error", None):
        raise RuntimeError(f"Supabase RPC error: {resp.error}")
    return resp.data or []


def format_context(chunks: List[dict]) -> str:
    """
    Format retrieved chunks into a context string for the LLM.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        title = chunk.get("title", "Unknown")
        content = chunk.get("content", "")
        context_parts.append(f"[Document {i}: {title}]\n{content}\n")
    return "\n---\n".join(context_parts)


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using the LLM with RAG context.
    """
    user_message = f"""Context Documents:
{context}

---

Question: {question}

Please answer the question based ONLY on the context documents provided above."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat_completion(
        messages=messages,
        model=LLM_MODEL,
        max_tokens=1024,
        temperature=0.3,  # Lower temperature for more factual responses
    )
    
    return response.choices[0].message.content


# --------- UI ----------
st.set_page_config(page_title="SAP Assistant", page_icon="🤖")
st.title("🤖 SAP Intelligent Assistant")

st.markdown(
    "Ask any question about SAP. I'll search my knowledge base and provide an answer based on relevant documentation."
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 View Sources"):
                for source in message["sources"]:
                    st.markdown(f"**{source['title']}** (similarity: {source['similarity']:.4f})")
                    st.caption(source['content'][:500] + "..." if len(source['content']) > 500 else source['content'])
                    st.divider()

# Chat input
if question := st.chat_input("Ask a question about SAP..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(question)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..."):
            try:
                # Step 1: Compute embedding for the question
                query_vector = compute_embedding(question)
                
                # Step 2: Search Supabase for relevant chunks
                chunks = search_supabase(query_vector, RESULTS_K)
                
                if not chunks:
                    answer = "I couldn't find any relevant documents in my knowledge base for your question. Please try rephrasing or ask about a different SAP topic."
                    sources = []
                else:
                    # Step 3: Format context from retrieved chunks
                    context = format_context(chunks)
                    
                    # Step 4: Generate answer using LLM
                    with st.spinner("🤔 Generating answer..."):
                        answer = generate_answer(question, context)
                    
                    # Prepare sources for display
                    sources = [
                        {
                            "title": chunk.get("title", "Unknown"),
                            "content": chunk.get("content", ""),
                            "similarity": chunk.get("similarity", 0.0)
                        }
                        for chunk in chunks
                    ]
                
                # Display answer
                st.markdown(answer)
                
                # Display sources
                if sources:
                    with st.expander("📚 View Sources"):
                        for source in sources:
                            st.markdown(f"**{source['title']}** (similarity: {source['similarity']:.4f})")
                            st.caption(source['content'][:500] + "..." if len(source['content']) > 500 else source['content'])
                            st.divider()
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This assistant uses **RAG (Retrieval-Augmented Generation)**:
    
    1. 🔍 **Search**: Your question is converted to embeddings and matched against our SAP knowledge base
    2. 📚 **Retrieve**: The most relevant document chunks are retrieved from Supabase
    3. 🤖 **Generate**: An LLM generates an answer based *only* on the retrieved documents
    
    This ensures answers are grounded in real documentation, not hallucinated!
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    st.caption(f"Embedding Model: `{EMBEDDING_MODEL}`")
    st.caption(f"LLM Model: `{LLM_MODEL}`")
    st.caption(f"Results per query: `{RESULTS_K}`")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
