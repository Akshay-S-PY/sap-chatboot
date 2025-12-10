# tools/agent.py
"""
Free LLM Agent for SAP Q&A
Supports multiple free LLM options:
1. Ollama (local, fully free, no internet)
2. Replicate (free tier, open models like Llama 2)
3. HuggingFace Inference API (free option)
"""

import os
from typing import List, Dict
import requests
import json
from datetime import datetime
try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None

class SAPAgent:
    def __init__(self, llm_provider="ollama", model="mistral"):
        """
        Initialize SAP Agent
        
        Args:
            llm_provider: "ollama", "replicate", or "huggingface"
            model: Model name (depends on provider)
                - ollama: "mistral", "neural-chat", "dolphin-mixtral"
                - replicate: "meta/llama-2-7b-chat"
                - huggingface: model ID
        """
        self.llm_provider = llm_provider
        self.model = model
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self):
        """System prompt for SAP expert"""
        return """You are an expert SAP consultant AI assistant. You help users with:
- SAP Basis administration
- SAP ABAP development
- SAP HANA database
- SAP Fiori and UI5
- SAP Security and Authorization
- SAP Configuration and Customization
- SAP Performance Tuning
- SAP Transport Management

Guidelines:
1. Provide accurate, practical advice based on SAP best practices
2. Always cite sources when answering from the knowledge base
3. Be clear and concise in your explanations
4. Include step-by-step instructions when relevant
5. Warn about potential risks or considerations
6. If unsure, say so and suggest consulting official SAP documentation

Format your responses clearly with:
- Key Points
- Step-by-step instructions (if applicable)
- Important Considerations/Warnings
- Related Topics"""
    
    def query_ollama(self, query: str, context: str = "") -> str:
        """Query local Ollama instance"""
        try:
            prompt = f"""Context from SAP Knowledge Base:
{context}

User Question: {query}

Please provide a helpful answer based on the context above."""
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": self.system_prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error from Ollama: {response.status_code}"
        
        except requests.exceptions.ConnectionError:
            return "❌ Ollama not running. Please start Ollama: `ollama serve`"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def query_replicate(self, query: str, context: str = "") -> str:
        """Query Replicate API (free tier available)"""
        try:
            api_token = os.getenv("REPLICATE_API_TOKEN")
            if not api_token:
                return "❌ REPLICATE_API_TOKEN not set. Get free token from https://replicate.com"
            
            prompt = f"""Context from SAP Knowledge Base:
{context}

User Question: {query}

Please provide a helpful answer based on the context above."""
            
            import replicate
            replicate.api.token = api_token
            
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            )
            
            return ''.join(output) if isinstance(output, list) else str(output)
        
        except ImportError:
            return "❌ Replicate not installed: `pip install replicate`"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def query_huggingface(self, query: str, context: str = "") -> str:
        """Query HuggingFace Inference API (free tier - recommended for HF Spaces)"""
        try:
            api_token = os.getenv("HF_API_TOKEN")
            if not api_token:
                return "❌ HF_API_TOKEN not set. Get free token from https://huggingface.co/settings/tokens (create with 'read' access)"
            
            prompt = f"""Context from SAP Knowledge Base:
{context}

User Question: {query}

Please provide a helpful answer based on the context above. Keep response concise and practical."""
            
            headers = {"Authorization": f"Bearer {api_token}"}
            
            # Map model names to HF Inference API model IDs
            model_mapping = {
                "mistral": "mistralai/Mistral-7B-Instruct-v0.1",
                "zephyr": "HuggingFaceH4/zephyr-7b-beta",
                "llama2": "meta-llama/Llama-2-7b-chat-hf",
                "neural-chat": "Intel/neural-chat-7b-v3-3"
            }
            
            model_id = model_mapping.get(self.model, self.model)
            api_url = f"https://api-inference.huggingface.co/models/{model_id}"
            
            # Use text generation task
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": 0.7,
                    "max_length": 1024,
                    "do_sample": True,
                    "top_p": 0.95
                }
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # HF returns list of dicts with 'generated_text' key
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '')
                    # Remove the prompt from the output
                    if text.startswith(prompt):
                        text = text[len(prompt):].strip()
                    return text if text else "No response generated"
                return str(result)
            elif response.status_code == 429:
                return "⏳ HuggingFace API rate limited. Please try again in a moment."
            elif response.status_code == 401:
                return "❌ Invalid HF_API_TOKEN. Check your token at https://huggingface.co/settings/tokens"
            else:
                error_msg = response.text
                return f"❌ HuggingFace API error {response.status_code}: {error_msg[:100]}"
        
        except requests.exceptions.Timeout:
            return "⏳ Request timed out. HuggingFace inference might be slow. Try again."
        except requests.exceptions.ConnectionError:
            return "❌ Connection error. Check internet connection."
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"
    
    def generate_answer(self, query: str, context: str = "") -> str:
        """Generate answer based on LLM provider"""
        if self.llm_provider == "ollama":
            return self.query_ollama(query, context)
        elif self.llm_provider == "replicate":
            return self.query_replicate(query, context)
        elif self.llm_provider == "huggingface":
            return self.query_huggingface(query, context)
        else:
            return f"❌ Unknown LLM provider: {self.llm_provider}"
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def format_response(self, answer: str, sources: List[Dict] = None) -> Dict:
        """Format response with sources and metadata"""
        response = {
            'answer': answer,
            'sources': sources or [],
            'timestamp': datetime.now().isoformat(),
            'model': self.model,
            'provider': self.llm_provider
        }
        return response


class SAGAAssistant:
    """Streaming RAG-Agent: Retrieval + Generation"""
    
    def __init__(self, rag_pipeline=None, llm_agent=None):
        """
        Args:
            rag_pipeline: RAG instance from embeddings.py
            llm_agent: SAPAgent instance
        """
        self.rag = rag_pipeline
        self.agent = llm_agent or SAPAgent()
    
    def answer(self, query: str, top_k: int = 5) -> Dict:
        """Answer user query with RAG + LLM"""
        
        # Step 1: Retrieve context
        if self.rag:
            context = self.rag.get_context(query, top_k=top_k)
            sources = self.rag.search(query, top_k=top_k)
        else:
            context = ""
            sources = []
        
        # Step 2: Generate answer
        answer = self.agent.generate_answer(query, context)
        
        # Step 3: Format response
        response = {
            'query': query,
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources),
            'model': self.agent.model,
            'provider': self.agent.llm_provider,
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 4: Add to history
        self.agent.add_to_history('user', query)
        self.agent.add_to_history('assistant', answer)
        
        return response


# Utility functions
def setup_agent(
    provider: str = "ollama",
    model: str = "mistral"
) -> SAPAgent:
    """Setup SAP agent"""
    return SAPAgent(llm_provider=provider, model=model)


if __name__ == "__main__":
    # Test agent
    agent = SAPAgent(llm_provider="ollama", model="mistral")
    
    test_query = "How do I monitor background jobs in SAP?"
    context = "SAP Background Jobs: Use transaction SM37 for job monitoring..."
    
    print("Testing SAPAgent with Ollama...")
    print(f"Query: {test_query}\n")
    
    response = agent.generate_answer(test_query, context)
    print(f"Response:\n{response}")
