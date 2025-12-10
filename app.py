# app.py
"""
SAP Intelligent Assistant - Streamlit UI
Free RAG-based Q&A system with local/cloud LLM support
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime

# Local imports
from tools.embeddings import RAGPipeline, load_rag_index
from tools.agent import SAPAgent, SAGAAssistant
import config

# ============== Page Configuration ==============
st.set_page_config(**config.STREAMLIT_PAGE_CONFIG)

# ============== Custom CSS ==============
st.markdown("""
<style>
    .main-title { font-size: 2.5em; color: #1f77b4; margin-bottom: 0.3em; }
    .subtitle { font-size: 1.2em; color: #666; margin-bottom: 2em; }
    .source-box { 
        background-color: #f0f2f6; 
        padding: 1em; 
        border-radius: 0.5em; 
        margin: 0.5em 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box { background-color: #d4edda; padding: 1em; border-radius: 0.5em; }
    .error-box { background-color: #f8d7da; padding: 1em; border-radius: 0.5em; }
    .warning-box { background-color: #fff3cd; padding: 1em; border-radius: 0.5em; }
</style>
""", unsafe_allow_html=True)

# ============== Session State Initialization ==============
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.rag = None
    st.session_state.agent = None
    st.session_state.messages = []
    st.session_state.system_ready = False

# ============== Helper Functions ==============
# ============== Helper Functions ==============
@st.cache_resource
def initialize_rag():
    """Load RAG pipeline - from HF Hub if in Spaces, else local"""
    try:
        # Check if running in HF Spaces
        hf_dataset_repo = os.getenv("HF_DATASET_REPO")
        running_in_hf_spaces = os.getenv("SPACE_ID") is not None
        
        if running_in_hf_spaces and hf_dataset_repo:
            st.info("📚 Loading from HuggingFace Hub...")
            try:
                rag = RAGPipeline()
                rag.load_from_hf_hub(hf_dataset_repo)
                st.success("✅ Vector search ready!")
                return rag
            except Exception as e:
                st.warning(f"⚠️ Could not load from HF Hub: {e}")
                st.info("Attempting local load...")
        
        # Fallback to local files
        if Path(config.INDEX_PATH).exists():
            st.info("📚 Loading vector search index...")
            rag = load_rag_index()
            st.success("✅ Vector search ready!")
            return rag
        else:
            st.warning("⚠️ RAG index not found. Please run the dataset builder first.")
            return None
    except Exception as e:
        st.error(f"❌ Error loading RAG: {e}")
        return None

@st.cache_resource
def initialize_agent():
    """Initialize LLM Agent"""
    try:
        agent = SAPAgent(
            llm_provider=config.LLM_PROVIDER,
            model=config.DEFAULT_MODEL
        )
        return agent
    except Exception as e:
        st.error(f"❌ Error initializing agent: {e}")
        return None

def initialize_system():
    """Initialize the entire system"""
    if st.session_state.initialized:
        return
    
    with st.spinner("Initializing SAP Assistant..."):
        st.session_state.rag = initialize_rag()
        st.session_state.agent = initialize_agent()
        st.session_state.system_ready = (
            st.session_state.rag is not None and 
            st.session_state.agent is not None
        )
        st.session_state.initialized = True
    
    return st.session_state.system_ready

def format_sources(sources):
    """Format sources for display"""
    if not sources:
        return "No sources found"
    
    html = ""
    for i, source in enumerate(sources, 1):
        html += f"""
        <div class='source-box'>
            <strong>Source {i}: {source.get('title', 'Unknown')}</strong><br>
            <small>📍 {source.get('source', 'unknown').upper()} | 
            Score: {source.get('score', 0):.2%}</small><br>
            <br>{source.get('full_text', '')[:300]}...
        </div>
        """
    return html

def get_answer(query: str):
    """Get answer from SAGA assistant"""
    if not st.session_state.system_ready:
        return None
    
    assistant = SAGAAssistant(
        rag_pipeline=st.session_state.rag,
        llm_agent=st.session_state.agent
    )
    
    response = assistant.answer(query, top_k=config.RAG_TOP_K)
    return response

# ============== Auto-Initialize System ==============
if not st.session_state.initialized:
    initialize_system()

# ============== Main UI ==============

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h1 class='main-title'>{config.TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{config.SUBTITLE}</p>", unsafe_allow_html=True)

with col2:
    # Show environment info
    running_in_hf = os.getenv("SPACE_ID") is not None
    llm_info = f"""
    **System Status:**
    - Provider: {config.LLM_PROVIDER}
    - Model: {config.DEFAULT_MODEL}
    - RAG: {'✅ Ready' if st.session_state.rag else '❌ Not loaded'}
    - Env: {'🤗 HF Spaces' if running_in_hf else '💻 Local'}
    """
    st.info(llm_info)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Initialize system
    if st.button("🚀 Initialize System"):
        initialize_system()
    
    st.divider()
    
    # LLM Settings
    st.subheader("🤖 LLM Settings")
    provider = st.selectbox(
        "LLM Provider",
        ["ollama", "replicate", "huggingface"],
        index=0
    )
    
    if provider == "ollama":
        model = st.selectbox("Model", list(config.OLLAMA_MODELS.keys()))
    elif provider == "replicate":
        model = st.selectbox("Model", list(config.REPLICATE_MODELS.keys()))
    else:
        model = st.text_input("HuggingFace Model ID", config.DEFAULT_MODEL)
    
    # RAG Settings
    st.subheader("📚 RAG Settings")
    top_k = st.slider("Top K Sources", 3, 10, config.RAG_TOP_K)
    chunk_size = st.slider("Chunk Size", 256, 1024, config.RAG_CHUNK_SIZE, step=128)
    
    st.divider()
    
    # Dataset Management
    st.subheader("📊 Dataset")
    
    if st.button("🔄 Rebuild Dataset"):
        st.info("Dataset building would run in terminal:")
        st.code("python tools/build_dataset.py")
    
    if st.button("🏗️ Build RAG Index"):
        st.info("Index building would run in terminal:")
        st.code("python tools/embeddings.py")
    
    # Help
    st.divider()
    st.subheader("❓ Help & Setup")
    
    help_topic = st.selectbox(
        "Setup Guide",
        ["Setup Ollama", "Setup Replicate", "Setup HuggingFace", "Deploy to HF Spaces", "FAQ"]
    )
    
    if help_topic == "Setup Ollama":
        st.markdown(config.HELP_MESSAGES["setup_ollama"])
    elif help_topic == "Setup Replicate":
        st.markdown(config.HELP_MESSAGES["setup_replicate"])
    elif help_topic == "Setup HuggingFace":
        st.markdown(config.HELP_MESSAGES["setup_huggingface"])
    elif help_topic == "Deploy to HF Spaces":
        st.markdown("""
        ### Deploy to HuggingFace Spaces
        
        **Free multi-user hosting!**
        
        1. **Prepare Data**
           - Create dataset repo on HF Hub
           - Upload FAISS index & metadata files
        
        2. **Push Code**
           - Push repo to GitHub
           - HF Spaces auto-syncs
        
        3. **Add Secrets**
           - `HF_API_TOKEN` - Your HF token
           - `HF_DATASET_REPO` - Your dataset repo ID
        
        4. **Deploy!**
           - Space auto-builds
           - Your URL: `huggingface.co/spaces/YOUR-NAME/sap-chatbot`
        
        📚 [See full guide](./DEPLOYMENT_HF_SPACES.md)
        """)
    else:
        st.markdown("""
        ### FAQ
        
        **Q: Can I use this offline?**
        A: Yes! Use Ollama for fully local operation.
        
        **Q: Is this free?**
        A: Yes! All components are free and open-source.
        
        **Q: How do I add more SAP knowledge?**
        A: Run `python tools/build_dataset.py` to scrape more sources.
        
        **Q: Can I deploy this?**
        A: Yes! Deploy on HuggingFace Spaces or Streamlit Cloud for free!
        
        **Q: How many users can access it?**
        A: Free tier supports ~5 concurrent users. Upgrade for more.
        
        **Q: How long does inference take?**
        A: First request: 30-60s. Subsequent: 10-20s. Faster on paid tiers.
        """)

# Main content area
if not st.session_state.system_ready:
    st.warning("⚠️ System not initialized. Click 'Initialize System' in the sidebar.")
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🚀 Initialize Now", use_container_width=True):
            if initialize_system():
                st.success("✅ System initialized!")
                st.rerun()
            else:
                st.error("❌ Failed to initialize system")
else:
    # Welcome message
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown(config.WELCOME_MESSAGE)
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Ask Me About SAP")
    
    # Display chat history
    for message in st.session_state.messages:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                st.write(message['content'])
    
    # Input
    user_query = st.chat_input("Ask a question about SAP...")
    
    if user_query:
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now().isoformat()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base and generating answer..."):
                response = get_answer(user_query)
                
                if response:
                    # Display answer
                    st.write(response['answer'])
                    
                    # Display sources
                    if response.get('sources'):
                        with st.expander("📚 Sources Used"):
                            st.markdown(
                                format_sources(response['sources']),
                                unsafe_allow_html=True
                            )
                    
                    # Add to history
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response['answer'],
                        'sources': response.get('sources'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Footer
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"🤖 Model: {response['model']}")
                    with col2:
                        st.caption(f"📊 Sources: {response['num_sources']}")
                    with col3:
                        st.caption(f"⏱️ {response['timestamp']}")
                else:
                    st.error("❌ Failed to generate response")

# Footer
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.markdown("**📖 [GitHub](https://github.com/Akshay-S-PY/sap-chatboot)**")
with footer_col2:
    st.markdown("**🔗 [SAP Community](https://community.sap.com)**")
with footer_col3:
    st.markdown("**⭐ Made with ❤️ by Akshay**")
        
        # Combine title and content for search
        text = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
        
        # Exact phrase matches
        if query in text:
            score += 20
            
        # Individual word matches
        query_words = query.split()
        matches = sum(1 for word in query_words if word in text)
        score += matches * 2
        
        # Title matches are more important
        title = doc.get('title', '').lower()
        if any(word in title for word in query_words):
            score += 10
            
        if score > 0:
            results.append((score, doc))
    
    # Sort by relevance
    results.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in results[:top_k]]

def format_answer(results, query):
    """Format the search results into a nice answer"""
    if not results:
        return "I couldn't find specific information about that topic in my knowledge base. Try asking about:\n\n- SAP Basis administration\n- System monitoring (SM50, SM66)\n- Transport Management (TMS)\n- User and security management\n- Background job processing"
    
    response = []
    response.append("## 📚 Found Information\n")
    
    for i, doc in enumerate(results, 1):
        title = doc.get('title', 'SAP Basis Article')
        content = doc.get('content', '')
        
        # Extract relevant snippet
        sentences = re.split(r'[.!?]+', content)
        snippet = '. '.join(sentences[:3]) + '.' if sentences else content[:300] + "..."
        
        response.append(f"**{i}. {title}**")
        response.append(f"{snippet}")
        response.append(f"*Source: {doc.get('url', 'SAP Community')}*")
        response.append("---")
    
    return "\n\n".join(response)

# Load dataset
dataset = load_dataset()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Number of results", 3, 10, 5)
    
    st.header("💡 Sample Questions")
    samples = [
        "How to monitor work processes?",
        "What is TMS in SAP?",
        "How to check system logs?",
        "User administration best practices",
        "Background job monitoring"
    ]
    
    for sample in samples:
        if st.button(sample, use_container_width=True):
            st.session_state.query = sample

# Main interface
if dataset:
    query = st.text_input(
        "💬 Ask your SAP Basis question:",
        placeholder="e.g., How do I analyze work processes using SM50?",
        value=st.session_state.get('query', '')
    )
    
    if st.button("🔍 Search", type="primary") or query:
        if query.strip():
            with st.spinner("Searching knowledge base..."):
                results = search_documents(query, dataset, top_k)
                st.markdown(format_answer(results, query))
else:
    st.error("No dataset available. Please check the configuration.")

# Footer
st.markdown("---")
st.caption("💡 This assistant uses publicly available SAP Community content. Always verify critical information with official SAP documentation.")
